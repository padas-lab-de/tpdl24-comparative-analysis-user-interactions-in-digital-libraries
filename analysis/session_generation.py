import openai
from analysis.utils import load_env_vars, get_mapping
from analysis.data_processing import session_to_human_readable

action_mapping = {
    "AdvancedSearch": ["goto_advanced_search", "search_advanced"],
    "AvailabilityButton": ["goto_local_availability"],
    "Chaining": [
        "search_change_sorting",
        "search_change_facets",
        "search_change_nohts",
    ],
    "ExternalLink": ["goto_google_books", "goto_google_scholar"],
    "FacetEvent": ["search_change_facets"],
    "GenericClick": ["goto_home", "search"],
    "GenericLink": ["goto_home", "search"],
    "GoogleBooksPreview": ["goto_google_books"],
    "PageView": ["goto_home"],
    "PaginationClick": ["search_change_paging"],
    "RecordAbstractToggle": ["view_description"],
    "RecordExport": ["export_bib", "export_cite", "export_mail"],
    "RecordMLT": ["view_doc_rec"],
    "RecordOrderForm": [],
    "RecordResultsScroller": ["search_change_paging"],
    "RecordSave": ["save_to_multiple_favorites", "save_search"],
    "RecordTab": ["search_change_facets"],
    "SearchHit": ["search"],
    "SearchHit2": ["search"],
    "SearchSubmit": ["search"],
    "SocialNet": ["export_search_mail"],
    "SpellingSuggestionClick": ["search_change_facets"],
}


def generate_synthetic_action(
    synthetic_topic, original_session, action_mappings=action_mapping
):
    openai.api_key = load_env_vars()
    system_prompt = {
        "role": "system",
        "content": "You are an intelligent assistant trained to generate synthetic user actions based on historical data of interactions with a digital library. Your responses should reflect plausible user actions that align with the given context of search and interaction patterns within an academic database. The list of actions the user can perform includes: "
        + ", ".join([mapping["action_label"] for mapping in action_mappings]),
    }

    few_shot_messages = [system_prompt]
    current_action_prompt = {
        "role": "user",
        "content": f"Query: {synthetic_topic} \n Context: {synthetic_topic}, Session: \n {original_session} \n The response should contain only a list of actions the user takes in the following format: \n Time spent: time_spent seconds; Action Type: action_type; Action Label: action_label, Params: params \n Note that you need to stop the search is the user information intent has been fulfilled. Each search action is done using only one search term at a time \n Response:",
    }
    few_shot_messages.append(current_action_prompt)

    response = openai.ChatCompletion.create(
        model="gpt-4", messages=few_shot_messages, temperature=0.2, max_tokens=2000
    )

    return response.choices[0].message.content


def create_synthetic_session(
    original_session, synthetic_topic, action_mappings, action_mapping=action_mapping
):
    for action in original_session["actions"]:
        action["action_type"] = get_mapping(action["action_type"], action_mapping)

    synthetic_response = generate_synthetic_action(
        synthetic_topic, session_to_human_readable(original_session), action_mappings
    )
    return synthetic_response
