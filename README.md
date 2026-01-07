# README 

This project is an AI Agent for pharmacies designed to help customers with queries about general medications' information, stock, and prescriptions of the customers. It is unable to sell medications or give medical advices.

The Agent is built using Python, Streamlit, and the OpenAI API

The Agent support Streaming, Multi-Step resoning and 2 languages: English and Hebrew.

## Architechture

1. **UI** - using Streamlit it maintains the chat interface and the session state (all the messages) 
1. **Agent** - Responsible for sending queries to OpenAI, handle the chunks it recieves via stream (and send them to the UI) and detect when tools need to be used, execute them and generate an answer using the information it got
1. **Tools** - A set of functions the Agent can use in order to extract data from the database and answer prompts of the users
4. **Database** - An API to extract data from the Database file (Json file)

## Running the Agent

To run the agent you need an **OpenAI API Key** written in **.env** file AND **Docker**.


### Installation and Running:

1. Clone the repo:
``` bash
git clone <repo_url>
cd PharmacyAgentAssignment
```

2. Set the OpenAI API Key in a .env file in the root folder:
```
OPENAI_API_KEY=...
```
3. You run the agent using a docker, in order to build and run it use these lines:
``` bash
docker build -t pharmacy-agent .

docker run -p 8501:8501 --env-file .env pharmacy-agent
```
In the terminal a URL will appear: 
```bash
URL: http://localhost:8501
```
Click on it in order to open the AI Agent's website.

### Tools the Agent can Use:

1. **get_medication_details(medication_name)**

	Gets details about a medication including active ingredients, dosage, and if it requires a prescription

2. **check_inventory(medication_name)**

	Checks the current stock level of a medication.

3. **validate_prescription(user_id, medication_name)**

	Checks if a user has a valid prescription for a specific medication.

4. **list_user_prescriptions(user_id)**

	Gets a list of all active prescriptions for a specific user.

## Multi Step Flows:
### 1. User checks if they should and can get a medicine
1.
	    Q: User asks what medicine they should take if a doctor told them they have a bacterial infection
2. 
    	Answer: Agent refuses to give medical advice and redirect to a medical professin
3. 
    	Q: User (is smart and remembers that Moxypen should reduce bacterial infections) asks the Agent if the have a prescription for Moxypen
4. 
    	Agent checks if the user has a prescription for that medicine (Tool -  validate_prescription) A: Yes or No depends on the Tool answer
5. 
    	Q: User asks if they have prescription for Azithromycin (a different medicine for bacterial infection) 
6. 
    	checks if the user has a prescription for that medicine(Tool - validate_prescription) and when using the tool it finds out the medicine doesn't exist in the database
    	A: Tells the user they don't have information about this medicine

### 2. User checks information about one of its medicines 
1.  
    	Q: User asks what are their prescriptions
2. 
    	Agent gets a list of active prescriptions of the user using the user ID (Tools - list_user_prescriptions)
    	A: list of the user perscribed medicines
3. 
    	Q: User asks about the usage of one of its medicines 
4. 
    	Agent checks info about the asked medicine (Tool - get_medication_details)
    	A: the usage of said medicine    
5. 
    	Q: User asks if they can order that medicine 
6. 
    	A: Agent refuse making a sale

### 3. User asks for information and stock of a medicine
1. 
    	Q: User asks about a specific medicine's active ingredients
2. 
	    Agent checks for medicine in database (Tool - get_medication_details) and
		A: Information about the medicine's active ingredients it got from the tool
3. 
		Q: User asks if the medicine is in stock
4. 
    	Agent gets the medicines stock (Tool)
    	A: The stock of the medicine it got from the tool
		(I found that sometimes the Agent would respond with Yes/No if the medicine is in stock and sometimes would also specify the stock - in images)


## Evaluation Plan:
We can evaluate our agent with multiple metrics.

1. **Adhering to its restrictions**
	
	__Description:__ Precentage of times the agent refused to give medical advices or try and sell medicines for customers.
	
	__goal:__ 100%
2. **Not Hallucinating**

	__Description:__ Precentage of times the Agent gave incorrect information (info about medicines, invented medicines not in the database, gave wrong stock number, etc.)
	
	__goal:__ 0%
3. **Using the correct tools**

	__Description:__ Precentage of times the Agent used the correct tool, this is a little tricky metric since the agent can sometimes use different tools to answer some questions (ususally about medicines that aren't in the database, sometimes it will used different tools in order to find information about a medicine)
	
	Example: If a user asks about an active prescription for a medicine that doesn't exist, the agent might use both validate_prescription and get_medication_details in order to answer and tell either they don't have a prescription or the medicine doesn't exist.
	
	__goal:__ strive to 100% (since we can still get correct answers when using different tools)
4. **extracting the correct information from the tools.**

	__Description:__ Precentage of times the Agent extracted the correct information from the tools it used
	
	__goal:__ 100%
5. **Managing multilingual flow?**
	
	__Description:__ Precentage of times the Agent succesfully translated/answered prompts in languages different then English with the same language
	
	__goal:__ 100%

6. **Memory Testing**

	__Description:__ using words like "it" or "that" after the first propmt to see if the agent remembers the context. Precentage of times the Agent succesfully answered questions with "vague" context to previous questions.

	__goal:__ 100%

7. **Typos Toleration**

	__Description:__ precentage of time the Agent answerd correctly to prompts that include typos like Akamol or Moxippen

	__goal:__ 100%