from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import traceback
from pymongo import MongoClient
import os

# Update the MongoClient to use the provided connection string
client = MongoClient("mongodb+srv://ihub:ihub@test-portal.lcgyx.mongodb.net/test_portal_db?retryWrites=true&w=majority")
db = client["test_portal_db"]  # Ensure this matches the database name in your connection string
questions_collection = db['Questions_Library']
temp_questions_collection = db['tempQuestions']
final_questions_collection = db['finalQuestions']

PROBLEMS_FILE_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'Frontend', 'public', 'json', 'questions.json')

def fetch_Questions(request):
    """
    Fetches questions from `tempQuestions`. If `tempQuestions` is empty,
    it fetches questions from `Questions_Library`, stores them in `tempQuestions`, 
    and then returns the questions from `tempQuestions`.
    """
    # Check if tempQuestions is empty
    temp_count = questions_collection.count_documents({})

    # If tempQuestions is empty, populate it from Questions_Library
    if temp_count == 0:
        # Fetch questions from Questions_Library
        documents = questions_collection.find({}, {'problems': 1, '_id': 0})
        problems = [problem for document in documents for problem in document.get('problems', [])]

        # Insert fetched data into tempQuestions
        questions_collection.insert_many([{"problems": problems}])

    # Retrieve and return the data from tempQuestions
    temp_documents = questions_collection.find({}, {'problems': 1, '_id': 0})
    temp_problems = [problem for document in temp_documents for problem in document.get('problems', [])]
    
    return JsonResponse({'problems': temp_problems})


from bson import ObjectId

def save_problem_data(new_problem):
    """
    Adds a new problem to the problems array in tempQuestions. If a document with ObjectId already exists,
    it appends the new problem to problems; otherwise, it creates a new document.
    """
    try:
        # Structure the problem data
        problem_data = {
            "id": new_problem.get('id'),
            "title": new_problem.get('title', ''),
            "role": new_problem.get('role', []),
            "level": new_problem.get('level', ''),
            "problem_statement": new_problem.get('problem_statement', ''),
            "samples": new_problem.get('samples', []),
            "hidden_samples": new_problem.get('hidden_samples', [])
        }
        
        # Convert the main document ID to ObjectId
        main_document_id = ObjectId('6731ed9e1005131d602865de')
        existing_document = questions_collection.find_one({'_id': main_document_id})

        if existing_document:
            # Append new problem to the problems array
            result = questions_collection.update_one(
                {'_id': main_document_id},
                {'$push': {'problems': problem_data}}
            )
            message = 'Problem added to existing document!'
        else:
            # Create a new document if it doesn’t exist, with the problems array initialized
            new_document = {
                "_id": main_document_id,
                "problems": [problem_data]
            }
            result = questions_collection.insert_one(new_document)
            message = 'New document created and problem added!'

        if result:
            return JsonResponse({
                'message': message,
                'problem_id': problem_data['id']
            }, status=201)
        else:
            raise Exception("Failed to save the document")

    except Exception as e:
        return JsonResponse({
            'error': f'Error saving problem data: {str(e)}'
        }, status=400)


@csrf_exempt
def publish_questions(request):
    """
    Moves questions from tempQuestions to finalQuestions with the contestId and visible_to passed in the request body.
    Appends to FinalQuestions collection instead of clearing it.
    """
    if request.method == 'POST':
        try:
            # Parse JSON data from the request to get contestId and visible_to
            data = json.loads(request.body)
            contest_id = data.get('contestId')
            visible_to = data.get('students', [])  # List of selected student regnos

            print("Received contestId:", contest_id)  # Debugging line
            print("Visible to students:", visible_to)  # Debugging line

            # Check if contest_id is provided
            if not contest_id:
                return JsonResponse({'error': 'contestId is missing in the request'}, status=400)

            # Retrieve questions from tempQuestions
            temp_questions = questions_collection.find({}, {'problems': 1, '_id': 0})

            # Extract problems from all documents in tempQuestions
            all_problems = []
            for document in temp_questions:
                all_problems.extend(document.get("problems", []))

            # Check if a document with the same contestId already exists
            existing_document = final_questions_collection.find_one({"contestId": contest_id})

            if existing_document:
                # Append problems to the existing document
                final_questions_collection.update_one(
                    {"contestId": contest_id},
                    {'$push': {'problems': {'$each': all_problems}}}
                )
                message = 'Questions appended to existing contest!'
            else:
                # Insert a new document with contestId, problems array, and visible_to
                final_questions_collection.insert_one({
                    "contestId": contest_id,
                    "problems": all_problems,
                    "visible_to": visible_to  # Store the list of student regnos
                })
                message = 'Questions published successfully!'

            return JsonResponse({'message': message}, status=200)

        except Exception as e:
            print("Error publishing questions:", str(e))
            traceback.print_exc()
            return JsonResponse({'error': 'Failed to publish questions'}, status=500)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)


@csrf_exempt
def modify_problem_data(new_problem):
    """
    Modifies an existing problem in `tempQuestions` based on its ID.
    """
    try:
        problem_id = new_problem.get("id")
        result = questions_collection.update_one(
            {'problems.id': problem_id},  # Match within the `problems` array by `id`
            {'$set': {'problems.$': new_problem}}  # Update the matched problem
        )
        
        if result.modified_count > 0:
            return JsonResponse({'message': 'Problem modified successfully!'}, status=200)
        else:
            return JsonResponse({'error': 'Problem not found or not modified'}, status=404)

    except Exception as e:
        print("Error modifying problem:", str(e))
        traceback.print_exc()
        return JsonResponse({'error': 'Failed to modify problem data'}, status=500)


def delete_problem_data(problem_id):
    """
    Deletes a problem from `tempQuestions` based on its ID within the `problems` array.
    """
    try:
        # Use `$pull` to remove the specific problem from the `problems` array
        result = questions_collection.update_one(
            {},  # Assuming there's only one document; otherwise, specify a filter if needed
            {'$pull': {'problems': {'id': problem_id}}}
        )

        if result.modified_count > 0:
            return JsonResponse({'message': 'Problem deleted successfully!'}, status=200)
        else:
            return JsonResponse({'error': 'Problem not found for deletion'}, status=404)

    except Exception as e:
        print("Error deleting problem:", str(e))
        traceback.print_exc()
        return JsonResponse({'error': 'Failed to delete problem data'}, status=500)


@csrf_exempt
def save_problem(request):
    """
    Handles saving, modifying, and deleting problems in `tempQuestions`.
    """
    if request.method == 'GET':
        return fetch_Questions(request)

    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            new_problem = data.get("problems", [])[0]
            return save_problem_data(new_problem)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            print("An error occurred:", str(e))
            traceback.print_exc()
            return JsonResponse({'error': str(e)}, status=500)

    elif request.method == 'PUT':
        try:
            data = json.loads(request.body)
            new_problem = data.get("problems", [])[0]
            return modify_problem_data(new_problem)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            print("An error occurred:", str(e))
            traceback.print_exc()
            return JsonResponse({'error': str(e)}, status=500)

    elif request.method == 'DELETE':
        try:
            print("entered")
            data = json.loads(request.body)
            problem_id = data.get("id")
            print(problem_id)
            return delete_problem_data(problem_id)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            print("An error occurred:", str(e))
            traceback.print_exc()
            return JsonResponse({'error': str(e)}, status=500)

    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)