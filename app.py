import os
import hashlib
from flask import Flask, request
import openai
import time

openai.api_key = os.getenv("OPENAI_KEY")


def leave_last_lines_from_file(filename,lines_count):
	with open(filename, encoding='utf-8') as file:
		lines = file.readlines()
		return ''.join(lines[-lines_count:])




app = Flask(__name__)



@app.route('/', methods=['POST'])
def main():

	delete_outdated_interactions()
	
	req = request.get_json(force=True)



	prompt = req.get('queryResult').get('queryText')


	dialogflow_session_id = req.get('session')


	encoded = dialogflow_session_id.encode()
	md5_hash = hashlib.md5(encoded).hexdigest()
	context_file = f"./talk_sessions/{md5_hash}.txt"


	if not os.path.isfile(context_file):
		file = open(context_file, 'w', encoding='utf-8')
		file.close()




	file = open(context_file, "a", encoding='utf-8')
	file.write(f"{prompt}\n")
	file.close()


	file = open(context_file, "r", encoding='utf-8')
	final_prompt =  file.read()
	file.close()


	gpt_response_text = get_gpt3_response(final_prompt)
	gpt_response_text = gpt_response_text.strip()





	file = open(context_file, "r", encoding='utf-8')

	if gpt_response_text in file.read():
		print("same answer was detected")
		gpt_response_text = get_gpt3_response(final_prompt)
		gpt_response_text = gpt_response_text.strip()





	file = open(context_file, "a", encoding='utf-8')
	file.write(f"{gpt_response_text}\n\n\n")
	file.close()


	last_lines_of_memory = leave_last_lines_from_file(context_file, 20)

	file = open(context_file, "w",  encoding='utf-8')
	file.write(f"{last_lines_of_memory}")
	file.close()



	if gpt_response_text == "":
		return {'fulfillmentText': "Sorry, I couldn't understand that"}
	else:
		return {'fulfillmentText': gpt_response_text}





def delete_outdated_interactions():
	three_minutes_ago = time.time() - 180
	folder = './talk_sessions/'

	for file in os.listdir(folder):
		print(file)
		t = os.stat(folder+file).st_mtime
		if t < three_minutes_ago:
			os.remove(folder+file)





def get_gpt3_response(final_prompt):
	response = openai.Completion.create(
		engine="text-davinci-001",
		prompt=f"{final_prompt}\n",
		temperature=0.5,
		max_tokens=100,
		top_p=1,
		frequency_penalty=0,
		presence_penalty=0)

	gpt_response_text = response.choices[0].text
	return gpt_response_text





if __name__ == '__main__':
	app.run(port=5000)
