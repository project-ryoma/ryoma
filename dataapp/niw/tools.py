from langchain.tools import tool, Tool


###
# This is a set of tools that can be used for preparing NIW (National Interest Waiver) application materials
# The tools are:
# - write_petition_letter
# - write_recommendation_letter
###


@tool
def write_petition_letter():
    """An NIW (National Interest Waiver) petition letter writer application"""
    return


@tool
def write_recommendation_letter():
    """A recommendation letter writer application"""
    return



tools = [

]