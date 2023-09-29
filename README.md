# Francis
SalesGPT for an AI travel agent specialising in group tours
I have adoped a similar approach to SalesGPT (https://github.com/filip-michalsky/SalesGPT)
There were a number of limitations to this approach which I have tried to mitigate:
- No direction to what details are gathered
- Had a tendancy to skip steps
- Chat history is stored locally and the whole chat history is passeed to the prompt
- Sample catalog is a simple text file.

## direction on whats gathered
use pydantic data classes to extract the relevant info from the conversation

## tendancy to skip step
define conversation steps and store list, again pydantic classes can be used t otrack where were at

## Chat storage
TBC - 

## Sample catalog is a simple text file
combineation of meta filters (where, when, how much & how long) to limit returns and the use sematic search on the day to day

## No returns for meta filters
return alternatives

