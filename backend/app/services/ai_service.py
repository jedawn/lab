from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import InMemorySaver
from app.core.config import settings
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END, MessagesState


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


def build_graph():
    llm = get_client()

    def llm_node(state: OverAllState) -> OverAllState:
        response = llm.invoke(state["messages"])
        return {"messages": [response]}

    def output_node(state: OverAllState) -> OverAllState:
        return {"output": state["messages"][-1].content}

    builder = StateGraph(OverAllState)
    builder.add_node("llm_node", llm_node)
    builder.add_node("output_node", output_node)
    builder.add_edge(START, "llm_node")
    builder.add_edge("llm_node", "output_node")
    builder.add_edge("output_node", END)

    checkpointer = InMemorySaver()
    return builder.compile(checkpointer=checkpointer)


# 延迟初始化:不在模块导入时创建,避免 API Key 未配置时整个应用无法启动
_graph = None


def get_graph():
    global _graph
    if _graph is None:
        _graph = build_graph()
    return _graph


async def chat(msg: str, thread_id: str) -> str:
    """非流式对话:返回完整回复(用 ainvoke 避免阻塞事件循环)"""
    graph = get_graph()
    config = {"configurable": {"thread_id": thread_id}}
    state = await graph.ainvoke({"messages": [HumanMessage(content=msg)]}, config=config)
    return state["output"]


async def chat_stream(msg: str, thread_id: str):
    """流式对话:逐 token 生成回复"""
    graph = get_graph()
    config = {"configurable": {"thread_id": thread_id}}
    async for chunk, _meta in graph.astream(
        {"messages": [HumanMessage(content=msg)]},
        config=config,
        stream_mode="messages",
    ):
        if chunk.content:
            yield chunk.content
