from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langgraph.graph import StateGraph, START, END, MessagesState
from psycopg.rows import dict_row
from psycopg_pool import AsyncConnectionPool


from app.core.config import settings
from langchain_openai import ChatOpenAI
from app.services.kb_service import query_kb
from app.services.lab_service import list_labs
from langchain_core.tools import tool
from rich import print as rprint
from typing import  Literal
from app.core.database import SessionLocal

SYSTEM_PROMPT = """
你是实验室知识库智能助手。
规则：
1. 回答问题必须优先调用知识库检索工具，严禁编造信息。
2. 如果知识库没有对应资料，如实告知用户暂无相关资料，不要猜测。
3. 回答尽量简洁，引用文档来源。
4. 只回答实验室相关业务问题。
以下是参考资料:
"""


class OverAllState(MessagesState):
    output: str


def get_client():
    if not settings.DASHSCOPE_API_KEY:
        raise ValueError("DASHSCOPE_API_KEY 未配置,请在 .env 中设置")
    return ChatOpenAI(
        api_key=settings.DASHSCOPE_API_KEY,
        base_url=settings.BASE_URL,
        model=settings.LLM_MODEL,
    )


# 进程级持久 checkpointer
# 注意:
# 1) 同步 PostgresSaver 不支持 astream/ainvoke(异步方法抛 NotImplementedError),必须用异步版
# 2) AsyncPostgresSaver.from_conn_string 是 async 上下文管理器,yield 的实例仅块内有效,
#    不适合进程级长驻;正确做法是传入 AsyncConnectionPool 连接池,每次操作借还连接
# 3) kwargs 与 from_conn_string 内部建连参数保持一致
_checkpointer = None


async def get_checkpointer():
    global _checkpointer
    if _checkpointer is None:
        if not settings.POSTGRES_URL:
            raise ValueError("POSTGRES_URL 未配置,请在 .env 中设置")
        pool = AsyncConnectionPool(
            settings.POSTGRES_URL,
            open=False,
            kwargs={"autocommit": True, "prepare_threshold": 0, "row_factory": dict_row},
        )
        await pool.open()
        _checkpointer = AsyncPostgresSaver(conn=pool)
        await _checkpointer.setup()  # 初始化表结构(幂等)
    return _checkpointer


# 延迟初始化:不在模块导入时创建,避免配置缺失时整个应用无法启动
_graph = None

@tool
def list_open_labs (keyword: str = "" ) -> str : 
    """查询当前开放中的实验室列表，可以按名称关键词筛选
    Args:
        keyword: 实验室名称关键词，为空时查询全部
    """
    db = SessionLocal()
    try :
        result = list_labs(db, keyword=keyword, page=1, page_size=50, status=1)
        labs = result[ "list" ] 
        if not labs: 
            return "没有找到符合条件的实验室" 
        lines = [ f" {i + 1 } . {lab[ 'name' ]} " for i, lab in enumerate (labs)] 
        return "已开启的实验室有:\n" + "\n" .join(lines) 
    finally :
        db.close()


tools = [list_open_labs]
async def get_graph():
    global _graph
    if _graph is None:
        llm = get_client()
        llm_with_tools = llm.bind_tools(tools)
        async def llm_node(state: OverAllState) -> dict:
            question = state[ "messages" ][- 1 ].content
            context_text = f"\n {query_kb(question)} \n"
            messages = [SystemMessage(content=f"{SYSTEM_PROMPT}{context_text}")] + state["messages"]
            response = await llm_with_tools.ainvoke(messages)
            rprint(response)
            return {"messages": [response]}

        def tool_node(state: OverAllState) -> dict:
            tools_by_name = {"list_open_labs": list_open_labs}
            last_msg = state["messages"][-1]
            for tool_call in last_msg.tool_calls:
                tool = tools_by_name[tool_call["name"]]
                tool_res = tool.invoke(tool_call["args"])
                tool_msg = ToolMessage(
                    name=tool_call["name"],
                    content=tool_res,
                    tool_call_id=tool_call["id"]
                )
                return {
                    "messages": tool_msg
                }
        def output_node(state: OverAllState) -> dict:
            return {"output": state["messages"][-1].content}

        def router(state: MessagesState) -> Literal[END, "tool_node"]:
            if state["messages"][-1].tool_calls:
                return "tool_node"
            else:
                return END

        builder = StateGraph(OverAllState)
        builder.add_node("llm_node", llm_node)
        builder.add_node("tool_node", tool_node)
        builder.add_node("output_node", output_node)
        builder.add_edge(START, "llm_node")
        builder.add_conditional_edges("llm_node", router, path_map=["tool_node", END])
        builder.add_edge("tool_node", "output_node")
        builder.add_edge("output_node", END)
        _graph = builder.compile(checkpointer=await get_checkpointer())
    return _graph


async def chat(msg: str, thread_id: str) -> str:
    """非流式对话:返回完整回复"""
    graph = await get_graph()
    config = {"configurable": {"thread_id": thread_id}}
    state = await graph.ainvoke({"messages": [HumanMessage(content=msg)]}, config=config)
    return state["output"]


async def chat_stream(msg: str, thread_id: str):
    """流式对话:逐 token 生成回复"""
    graph = await get_graph()
    config = {"configurable": {"thread_id": thread_id}}
    async for chunk, _meta in graph.astream(
        {"messages": [HumanMessage(content=msg)]},
        config=config,
        stream_mode="messages",
    ):
        if chunk.content:
            yield chunk.content
