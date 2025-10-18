"I want to port this to run as a api enpoint on cloudflare workers: https://developers.cloudflare.com/workers/languages/python/

The endpoint should accept a product image and a list of demographic profiles and elicit responses from the llm and return a list of the responses in order, a list of the pmf distributions in order and a list of the mean pmfs in order"

"Okay lets fix some misunderstandings. The endpoint will receive a request like this: {
"image": "base64_encoded_image_data",
"demographic_profiles": [
{
"age": 32,
"gender": "female",
"income": "$72k",
"location": "San Francisco",
"occupation": "software engineer",
"education": "bachelor's",
"interests": ["hiking", "yoga", "tech gadgets"]
},
{
"age": 54,
"gender": "Male",
"income": "$50k",
"location": "San Antonio",
"occupation": "Mechanical engineer",
"education": "Master's",
"interests": ["Running", "beer", "knifes"]
}, ...
]
}

and from there should return {
"responses": [
{
"response1": "First LLM response...",
"response2": "Second LLM response..."
}
],
"pmf_distributions": [
[[0.1, 0.2, 0.3, 0.25, 0.15], ...]
],
"mean_pmfs": [3.45, 3.67, ...],
"overall_statistics": {
"mean": 3.56,
"std": 0.45,
"min": 2.89,
"max": 4.23
}
}"

"lets change the endpoint to just accept one demographic and create one synthetic customer"

"we expect to receive the image as base64, so let us remove helper functions that encode the image etc"

"I am working on porting my fastapi endpoint to work with cloudflare workers. I have been trying to make it work for a while so #file:worker.py is a bit convoluted and might be completely wrong. I cannot really depend on external libraries since workers python is quite experimental for now from cloudflares side. Go through the whole #codebase to familiarise yourself with the project (everything in src is really just helper functions that the api call. Most importantly the endpoint creates a synthetic consumer based on the demographic profile provided with the post request, and then the ssr_rater generates the likert distribution based on the response from the synthetic consumer). Then I want you to make sure #file:worker.py contains only the necessary code to wrap the endpoint in app.py so that it is compatible with cloudflare workers. I will include some of the documentation so you can make sure you get it right: #fetch https://developers.cloudflare.com/workers/languages/python/ https://developers.cloudflare.com/workers/languages/python/packages/
https://github.com/cloudflare/workers-py?tab=readme-ov-file#pywrangler"

"I am planning to have the frontend and typescript backend separate from the evaluation api worker so that I can deploy them separatly. Suggest how I should change the structure of the project to accomodate this and ensure deployment is easy and coherent"

"yes i like the first structure. Lets move the existing files into the api folder and create the other folders before we start writing any code. Once we have created the structure I want to run (myself) the api again to ensure it still works as intended"

"Help me set up the frontend with svelte and sveltekit"

"Help me plan how we should set up the typescript backend to integrate the python api and use the durable object to manage sessions"

"Create a bash script to start the individual services (api, backend, frontend)"

"Keep the script significantly simpler. Do not include terminal formatting or other fluff"