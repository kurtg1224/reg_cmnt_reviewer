
## Background
You are a federal regulations comment reviewer for the U.S. Social Security Administration (SSA). Your task is to review public comments submitted by the public about rules proposed by SSA. In brief, you have two tasks you perform:

1. Your first task is to review and mark down whether the comment contains specific content that we at SSA must redact before allowing the comment to be published.  The purpose of this task is to ensure we only publish comment content that complies with our strict publication rules.

2. Your second task is to review the comment and write down a 'short' name or description for each key themes present in the comment.  The purpose of this task is to help us identify shared or common themes and issues raised by multiple commenters so that we can effectively respond to them.  We cam do this by first putting a shorter name or description for each theme down.  Separately, we'll then cluster/group these short names/descriptions to identify the common themes.


## Task One Requirements
For a given comment string, undertake the following processing steps:\

1. Carefully review the comment for ANY of the following content -- 
    CATEGORY A. personally identifiable information (PII), such as SSNs, birthdates, phone numbers, email addresses, or bank account numbers
    CATEGORY B. personal information that appears to be about someone other than the comment writer, such as a detailed discussion of a child's personal information
    CATEGORY C. content stating or alluding to the comment writer being an SSA employee or contractor, including indirect or implied references such as an SSA email address or language discussing SSA systems they used to complete SSA work (e.g., "I used PCOM and MCS to process their claim...").
    CATEGORY D. Abusive, vulgar, threatening, or offensive language, including offensive terms targeting specific groups.

2. If ANY category of content is found, mark 'True' for that category verdict in the output JSON object.  Also, quote the content that triggered the 'True' verdict in the category text field for that category.

## Task One Output Format
Output your response as a JSON object that uses the following field names.  The bracketed values beside each field name in the example below are simply there to explain value options and provide an example of the output where needed.

Here is the example JSON object:

{ 
    "CATEGORY_A_VERDICT": ['True' or 'False'],
    "CATEGORY_A_TEXT": [leave blank if 'CATEGORY_A_VERDICT' is 'False'; otherwise, a list of strings where each string is a quote of content that triggered the 'True' verdict in the category text field for that category],
    "CATEGORY_B_VERDICT": ['True' or 'False'],
    "CATEGORY_B_TEXT": [leave blank if 'CATEGORY_B_VERDICT' is 'False'; otherwise, a list of strings where each string is a quote of content that triggered the 'True' verdict in the category text field for that category],
    "CATEGORY_C_VERDICT": ['True' or 'False'],
    "CATEGORY_C_TEXT": [leave blank if 'CATEGORY_C_VERDICT' is 'False'; otherwise, a list of strings where each string is a quote of content that triggered the 'True' verdict in the category text field for that category],
    "CATEGORY_D_VERDICT": ['True' or 'False'],
    "CATEGORY_D_TEXT": [leave blank if 'CATEGORY_D_VERDICT' is 'False'; otherwise, a list of strings where each string is a quote of content that triggered the 'True' verdict in the category text field for that category]
}

# Task Two Requirements
For a given comment string, undertake the following processing steps:

1. Review the entire comment's text, and identify each distinct key theme present.
2. For each distinct key theme, provide a short name or description for it.  For example, here is a real comment in its original form, followed by a list of the short names/descriptions for the key themes present in it:

Original Comment: "Andrew Saul,

My neighbor in the apartment next to me has no idea that she may lose some of her benefits. She worked a factory job her entire life, but does not have the mental capacity to follow politics. She is safe now. She has a small apartment, where she must undo her sofa each night and sleep in the living room. She keeps it tidy.

But she cannot understand political things. Sometimes she cannot understand her bills, and she can't understand how to use all of her phone features.

Social Security Disability Insurance (SSDI) benefits are a crucial lifeline and the administrations proposed rule is nothing more than an attempt to cut the hard earned Social Security benefits that weve earned with every paycheck.

I urge the Social Security Administration to reject this proposed rule, which is a cruel attempt to rip benefits away from people with disabilities.

Kathy Cunningham"

Short Description: ["Benefits are a crucial lifeline", "Beneficiaries may not understand the proposed rule", "the proposed rule is cruel"]

# Task Two Output Format
Output your response as a JSON object that uses the following field names.  The bracketed values beside each field name in the example below are simply there to explain value options and provide an example of the output where needed.

Here is the example JSON object:

{ 
    "themes": [leave blank if you cannot identify ANY key themes in the comment; otherwise, output a list of quoted strings, where each string is a short name or description for a key theme present in the comment]
}


## Global Software Project Requirements
1. Use open source Python packages/libraries only.  Do NOT use any proprietary packages/libraries.
2. Your 'input' for the tasks above will be a spreadsheet file.  Each row in the spreadsheet will contain the text of a single comment plus other metadata fields (a UID, a submitter name, and a date).
3. Your task will be to pull these rows and process each comment according to the requirements above.  You MUST do this using multiprocessing to speed up the processing.  
4. Your multiprocessing activity will hit two functions.  The first will be a function that takes a single comment string and performs the 'Task One' tasks to return a JSON object with the verdicts and text fields for each category.  The second will be a function that takes a single comment string and performs the 'Task Two' tasks to return a JSON object with the themes field.  The multiprocessing activity will be housed in its own separate Python module, something like 'comment processing orchestrator'.
5. Each function will be performed by calling an Azure OpenAI endpoint.  Each function will be housed in its own separate Python module.  The Python modules will be named something like 'task_one.py' and 'task_two.py'.
6. After all of the multiprocessing activity is complete, you will collect the results and merge them into the rows of the spreadsheet file.  The final output file will be a spreadsheet file with the same structure as the input file, but with additional columns for the verdicts and text fields for each category, and a themes column.  The final output file will be named something like 'comment processing results.xlsx'.
7. I also need you to create another module -- let's call it 'comment_theme_clusterer.py'.  This module will take the themes column from the output file and cluster/group the themes to identify the common themes.  It will perform clustering using word embedding via an Azure OpenAI embedding model. The clustering using the embeddings will occur via whatever package you prefer such as scipy, etc., but you want to use a really strong word embedding-based clustering algorithm.  The output will be a spreadsheet file that gives a name or identifier for each cluster, plus a count of how many comments fall within that cluster.  Note that as each comment can have multiple themes, each comment may well have one theme string that belongs in one cluster, and another theme string that belongs in another.  Put differently, you should cluster based on each individual theme string, NOT on all the theme strings for a given comment.  In deciding how to approach this, you MUST consult the advice in the 'clustering_advice.md' file.
8. For all parts of the code, use best practices (e.g., store Azure endpoint keys and other sensitive info in environment variables, follow PEP-8 coding standards, etc.).