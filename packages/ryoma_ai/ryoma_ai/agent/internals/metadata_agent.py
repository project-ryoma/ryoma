# metadata_agent.py
from typing import Dict, Any
from ryoma_ai.agent.chat_agent import ChatAgent


class MetadataSummarizationAgent(ChatAgent):
    def summarize_column(self,
                         column_name: str,
                         profile: Dict[str, Any]) -> str:
        prompt = f"""
        Column Name: {column_name}
        Type: {profile.get('type')}
        Null Ratio: {profile.get('null_ratio'):.2f}
        Distinct Count: {profile.get('distinct_count')}
        """
        if 'min' in profile:
            prompt += f"Min: {profile['min']}, Max: {profile['max']}, Mean: {profile['mean']:.2f}\n"
        if 'sample_values' in profile:
            prompt += f"Sample Values: {profile['sample_values']}\n"
            prompt += f"Min Length: {profile['min_length']}, Max Length: {profile['max_length']}\n"

        prompt += "\nDescribe what this column likely represents."

        return self.chat(prompt).content

    def summarize_schema(self,
                         schema_profile: Dict[str, Dict[str, Any]]) -> Dict[str, str]:
        return {
            column: self.summarize_column(column, profile)
            for column, profile in schema_profile.items()
        }
