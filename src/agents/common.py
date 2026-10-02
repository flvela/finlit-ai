"""list of common agent node functions"""
from langchain.messages import AIMessage


from agents.state import MESSAGES_FIELD, OUTPUT_FIELD, FinLitState


def get_output_state(state: FinLitState, llm_result: AIMessage, messages):
  """returns the output state based on given input state, llm result and messages"""
  if llm_result.tool_calls:
    return {MESSAGES_FIELD: [*messages, llm_result] if not state.get(MESSAGES_FIELD) else [llm_result]}

  output_text = llm_result.content
  if isinstance(llm_result.content, list):
    content = llm_result.content[0]
    if isinstance(content, dict) and 'text' in content:
      output_text = content['text']

  return {OUTPUT_FIELD: output_text, MESSAGES_FIELD: [AIMessage(content=llm_result.content)]}
