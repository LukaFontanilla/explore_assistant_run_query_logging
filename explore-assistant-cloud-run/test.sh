#!/bin/bash

# Load environment variables from .env file
if [ -f .env ]; then
  while IFS= read -r line; do
    if [[ ! "$line" =~ ^# && "$line" =~ = ]]; then
      export "$line"
    fi
  done < .env
fi

# Check if URL is provided
if [ -z "$1" ]; then
  echo "Usage: $0 <cloud_run_url>"
  exit 1
fi

URL=$1

# Make the curl request
curl -X POST "$URL" \
-H "Content-Type: application/json" \
-d '{"contents":"The current date is 8/21/2025, 2:05:09 PM\n    \n    \n    \n    \n      Primer\n      ----------\n      A user is iteractively asking questions to generate an explore URL in Looker. The user is refining his questions by adding more context. The additional prompts he is adding could have conflicting or duplicative information: in those cases, prefer the most recent prompt. \n\n      Here are some example prompts the user has asked so far and how to summarize them:\n\n- The sequence of prompts from the user: \"make a chart of sales by region\", \"make it a an area chart\", \"make it a table\". The summarized prompts: \"make a chart of sales by region make it a table\"- The sequence of prompts from the user: \"show me sales by region\", \"by product\". The summarized prompts: \"show me sales by region and product\"\n\n      Conversation so far\n      ----------\n      input: \"total sales all time\"\n    \n      Task\n      ----------\n      Summarize the prompts above to generate a single prompt that includes all the relevant information. If there are conflicting or duplicative information, prefer the most recent prompt.\n\n      Only return the summary of the prompt with no extra explanatation or text\n        \n    \n    ","parameters":{}}'