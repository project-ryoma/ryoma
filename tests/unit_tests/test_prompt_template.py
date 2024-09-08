from ryoma_ai.prompt.prompt_template import PromptTemplateFactory


def test_base_prompt_template():
    ryoma_prompt = PromptTemplateFactory()
    ryoma_prompt.set_base_prompt("This is a test prompt.")
    template = ryoma_prompt.build_prompt()
    messages = template.format_messages()
    assert messages[0].content == "This is a test prompt."


def test_prompt_template():
    ryoma_prompt = PromptTemplateFactory()
    ryoma_prompt.add_context_prompt(
        "You are provided with the following context: {prompt_context}"
    )
    template = ryoma_prompt.build_prompt()
    messages = template.format_messages(prompt_context="This is a test context.")
    assert (
        messages[1].content
        == "You are provided with the following context: This is a test context."
    )
