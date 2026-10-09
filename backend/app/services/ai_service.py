from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langgraph.graph import StateGraph, START, END, MessagesState
from psycopg.rows import dict_row
from psycopg_pool import AsyncConnectionPool

from app.core.config import settings
from langchain_openai import ChatOpenAI
from app.services.kb_service import query_kb

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


async def get_graph():
    global _graph
    if _graph is None:
        llm = get_client()

        async def llm_node(state: OverAllState) -> dict:
            messages = [SystemMessage(content=SYSTEM_PROMPT)] + state["messages"]
            response = await llm.ainvoke(messages)
            return {"messages": [response]}

        def output_node(state: OverAllState) -> dict:
            return {"output": state["messages"][-1].content}

        builder = StateGraph(OverAllState)
        builder.add_node("llm_node", llm_node)
        builder.add_node("output_node", output_node)
        builder.add_edge(START, "llm_node")
        builder.add_edge("llm_node", "output_node")
        builder.add_edge("output_node", END)
        _graph = builder.compile(checkpointer=await get_checkpointer())
    return _graph


async def chat(msg: str, thread_id: str) -> str:
    """非流式对话:返回完整回复"""
    graph = await get_graph()
    global SYSTEM_PROMPT
    SYSTEM_PROMPT = f"{SYSTEM_PROMPT}{query_kb(msg)}"
    config = {"configurable": {"thread_id": thread_id}}
    state = await graph.ainvoke({"messages": [HumanMessage(content=msg)]}, config=config)
    return state["output"]


async def chat_stream(msg: str, thread_id: str):
    """流式对话:逐 token 生成回复"""
    global SYSTEM_PROMPT
    SYSTEM_PROMPT = f"{SYSTEM_PROMPT}{query_kb(msg)}"
    graph = await get_graph()
    config = {"configurable": {"thread_id": thread_id}}
    async for chunk, _meta in graph.astream(
        {"messages": [HumanMessage(content=msg)]},
        config=config,
        stream_mode="messages",
    ):
        if chunk.content:
            yield chunk.content
