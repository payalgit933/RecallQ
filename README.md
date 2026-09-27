# RecallQ — Intelligent Personal File Search System

**Project Type:** MCA Mini Project
**Project Status:** Under Development
**Team Size:** 3 Members
**Project Repository:** [RecallQ on GitHub](https://github.com/payalgit933/RecallQ)

---

## 1. Project Overview

RecallQ is an intelligent personal file search system designed to help users find documents when they cannot remember the exact filename, folder location, or words used inside a document.

Users often store important information in PDFs, Word documents, notes, and text files. Finding a particular document later can be difficult when many files have similar names or when the user remembers only a small part of the information.

RecallQ aims to solve this problem by allowing users to search for files using the information they remember. The system will display relevant documents and explain why each result matches the search query.

**Example:**

A user remembers that an Infosys eligibility document mentioned a minimum of 60% marks but cannot remember its filename.

Instead of manually opening multiple files, the user can search:

> Find the Infosys eligibility document that mentions 60% marks.

RecallQ will search the available documents, display matching results, and show the text that helped identify each document.

---

## 2. Problem Statement

As the number of digital documents increases, users often struggle to locate specific information stored across multiple files and folders.

Traditional file search commonly depends on filenames, folder locations, or exact keywords. This can make it difficult to find a document when the user remembers its contents but not its name.

Therefore, a system is needed that can search document contents, identify relevant files, rank the results, and explain why a particular file matches the user's query.

---

## 3. Project Objectives

* Develop a simple interface for searching personal documents.
* Allow users to upload supported document files.
* Extract and process text from documents.
* Search document contents using keywords and phrases.
* Rank matching documents according to their relevance.
* Display a relevant text snippet explaining each match.
* Store document information and extracted text in a database.
* Extend the system with semantic search to identify related meanings, even when exact keywords differ.
* Provide a user-friendly and maintainable application.

---

## 4. Proposed Features

### Phase 1 — Basic Search (MVP)

The Minimum Viable Product (MVP) is the smallest working version of RecallQ.

* Search text files using keywords.
* Display matching filenames.
* Show the matching text snippet.
* Display the file location when available.
* Explain why the result matched the query.

### Phase 2 — Document Processing

* Upload TXT files.
* Extract text from PDF files.
* Extract text from DOCX files.
* Store file metadata and extracted text.
* Handle unsupported files and extraction errors.

### Phase 3 — Database Integration

* Store file names, paths, file types, and extracted text in MySQL.
* Retrieve document information during searches.
* Prevent duplicate records where practical.
* Allow users to remove document records and manage indexed files.

### Phase 4 — Semantic Search

* Convert document text and search queries into numerical representations called embeddings.
* Compare the meaning of the query with the meaning of stored document content.
* Rank semantically relevant results.
* Combine keyword matching and semantic similarity where appropriate.
* Display a human-readable explanation for each result.

Semantic search is a planned enhancement; it will be implemented and tested after basic keyword search works.

### Phase 5 — Frontend and Integration

* Build a React user interface.
* Add a search bar and file upload component.
* Display ranked results and match explanations.
* Connect the frontend to the Flask backend using REST APIs.
* Test the complete application.

---

## 5. Technology Stack

| Component               | Technology                                          | Purpose                                    |
| ----------------------- | --------------------------------------------------- | ------------------------------------------ |
| Frontend                | React.js with Vite                                  | User interface                             |
| Styling                 | CSS / Bootstrap                                     | Responsive design                          |
| Backend                 | Python with Flask                                   | Application logic and APIs                 |
| Database                | MySQL                                               | Store document metadata and extracted text |
| File processing         | Python libraries                                    | Extract text from supported files          |
| PDF processing          | PyMuPDF or another suitable PDF library             | Read PDF text                              |
| DOCX processing         | python-docx                                         | Read Word document text                    |
| Semantic search         | Sentence Transformers or a suitable embedding model | Find related meanings                      |
| Version control         | Git                                                 | Track code changes                         |
| Code hosting            | GitHub                                              | Collaborate and review changes             |
| API testing             | Postman                                             | Test backend endpoints                     |
| Development environment | VS Code                                             | Write and run code                         |

The exact libraries and versions will be finalized during implementation.

---

## 6. System Workflow

The planned workflow is:

1. The user uploads supported documents.
2. The backend validates the uploaded files.
3. The file-processing module extracts text from each document.
4. The system stores document information and extracted text in MySQL.
5. The user enters a search query.
6. The frontend sends the query to the Flask backend.
7. The search module compares the query with indexed documents.
8. The system ranks relevant results.
9. The frontend displays filenames, relevant text snippets, and match explanations.
10. The user can identify and open the relevant document.

**Planned architecture:**

```
User
  |
  v
React Frontend
  |
  | HTTP / REST API
  v
Flask Backend
  |
  +---- File Processing Module
  |
  +---- Search and Ranking Module
  |
  +---- Semantic Search Module (later phase)
  |
  v
MySQL Database
  |
  v
Ranked Results and Match Explanations
  |
  v
React Frontend
```

---

## 7. Project Folder Structure

We will develop the application using separate frontend and backend folders.

```
RecallQ/
|
|-- frontend/
|   |-- src/
|   |-- public/
|   |-- package.json
|   |-- index.html
|   `-- vite.config.js
|
|-- backend/
|   |-- app.py
|   |-- routes/
|   |-- services/
|   |-- database/
|   |-- uploads/
|   |-- requirements.txt
|   `-- .env.example
|
|-- docs/
|   |-- project-plan.md
|   |-- api-documentation.md
|   `-- testing.md
|
|-- .gitignore
`-- README.md
```

This is the planned structure. Folders and files will be created when the corresponding development stage begins.

* `frontend/`: React components, pages, styling, and API integration.
* `backend/`: Flask application and API routes.
* `backend/services/`: File extraction, search, and ranking logic.
* `backend/database/`: Database connection and database operations.
* `backend/uploads/`: Local uploaded files during development; actual user files will not be committed to GitHub.
* `docs/`: Project planning, API documentation, and testing records.
* `.gitignore`: Prevent local configuration, secrets, environments, and uploaded files from being committed.

---

## 8. Team Members and Responsibilities

The team has three members. Each member will own a major area while coordinating with the other members.

### Member 1 — Payal Kumari: Backend and Integration

**Primary responsibility:** Flask backend and integration of application components.

Tasks:

* Set up the Flask application.
* Learn Flask routes and REST API fundamentals.
* Implement the search API.
* Develop keyword matching and result ranking with explanations.
* Coordinate frontend-backend integration.
* Test APIs using Postman.
* Review pull requests and help resolve integration issues.

Initial branch: `payal`

### Member 2 — Frontend Developer

**Primary responsibility:** React user interface.

Tasks:

* Set up the React project using Vite.
* Create the home page and search interface.
* Build the search bar and upload form.
* Design the search results list.
* Display filenames, text snippets, and match explanations.
* Add loading, empty-result, and error states.
* Connect the interface to Flask APIs.
* Test the interface with different queries and results.

Initial branch: `member2`

### Member 3 — File Processing and Database Developer

**Primary responsibility:** Document extraction and data storage.

Tasks:

* Research text extraction from TXT, PDF, and DOCX files.
* Implement document validation and text extraction.
* Design the MySQL database schema.
* Create tables and database operations.
* Store document metadata and extracted text.
* Handle unsupported files, empty documents, and extraction errors.
* Coordinate with the backend developer on how extracted documents will be searched.

Initial branch: `member3`

**Team rule:** Responsibilities identify ownership, not isolation. All members should understand the overall workflow, review one another's work, and help test the complete application.

---

## 9. Git and GitHub Collaboration Workflow

We will use Git branches so team members can work independently without immediately changing the shared `main` branch.

### Main branches

* `main`: Shared, integrated project code.
* `payal`: Payal's working branch.
* `member2`: Member 2's working branch.
* `member3`: Member 3's working branch.

Each member should normally work on their own branch. Additional feature branches can be created when necessary.

### Step 1 — Clone the repository

Each teammate should accept the GitHub collaborator invitation, install Git, configure their Git identity, and clone the repository.

```
git clone https://github.com/payalgit933/RecallQ.git
cd RecallQ
```

Open the cloned folder in VS Code.

### Step 2 — Create a personal branch

Each member should create their own branch from the latest `main` branch.

```
git switch main
git pull origin main
```

Payal:

```
git switch -c payal
```

Member 2:

```
git switch -c member2
```

Member 3:

```
git switch -c member3
```

If your personal branch already exists, switch to it instead of creating it again:

```
git switch your-branch-name
```

Replace `your-branch-name` with your actual branch name.

### Step 3 — Make and commit changes

After making a small, focused change, check its status:

```
git status
```

Stage and commit the relevant files:

```
git add .
git commit -m "Describe your changes"
```

Use a clear commit message that describes the change.

### Step 4 — Push your branch

Payal:

```
git push -u origin payal
```

Member 2:

```
git push -u origin member2
```

Member 3:

```
git push -u origin member3
```

The `-u` option sets the upstream branch for the first push. Subsequent pushes can normally use `git push`.

### Step 5 — Create a pull request

On GitHub:

1. Open the RecallQ repository.
2. Select Pull requests.
3. Click New pull request.
4. Set the base branch to `main`.
5. Set the compare branch to the branch containing your changes.
6. Review the changes and create the pull request.
7. Ask another team member to review it.
8. Merge the pull request after the changes are approved and tested.

### Step 6 — Update the local main branch

After a pull request is merged, each member should update their local `main`:

```
git switch main
git pull origin main
```

Before starting a new task, create a new working branch from the updated `main`, or update your existing feature branch carefully.

### Important Git rules

* Save your work before switching branches.
* Commit only the changes you intend to include.
* Do not commit `.env` files, API keys, passwords, virtual environments, or uploaded user documents.
* Avoid having multiple people edit the same files unnecessarily.
* Pull requests should target `main`.
* Do not force-push shared branches.
* If a merge conflict occurs, discuss it with the team before resolving it.
* Do not merge unfinished or untested features into `main`.

---

## 10. Development Roadmap

We will complete the project in small, testable milestones.

| Milestone | Work                           | Completion criteria                                                |
| --------- | ------------------------------ | ------------------------------------------------------------------ |
| 1         | Project planning and Git setup | Shared README, working branches, and team workflow                 |
| 2         | Backend and frontend skeletons | Flask and React applications run locally                           |
| 3         | Basic keyword search           | Search finds matching text in sample TXT files                     |
| 4         | Search result explanations     | Results display relevant matching snippets                         |
| 5         | PDF and DOCX support           | Text is extracted from supported documents                         |
| 6         | MySQL integration              | Document metadata and extracted text are stored and retrieved      |
| 7         | Frontend integration           | Search interface works with the Flask API                          |
| 8         | Semantic search                | Related-meaning queries can retrieve relevant documents            |
| 9         | Testing and error handling     | Main workflows and common errors are tested                        |
| 10        | Documentation and presentation | Final report, screenshots, workflow diagram, and demo are prepared |

The milestones may be adjusted based on progress and project deadlines.

---

## 11. Initial MVP Scope

To avoid making the first version too complicated, the first working version will support:

* A few sample TXT documents.
* A basic keyword search input.
* Case-insensitive text matching.
* A list of matching filenames.
* A short matching text snippet.
* A simple explanation of why each result was returned.

The initial MVP does not require semantic search, authentication, cloud deployment, or advanced AI features. Those can be considered after the basic workflow is functional.

---

## 12. Testing Plan

We will test the system using realistic cases.

| Test case                          | Expected behaviour                                                           |
| ---------------------------------- | ---------------------------------------------------------------------------- |
| Search for an existing word        | Matching documents are displayed                                             |
| Search with different letter cases | Case-insensitive matches are found                                           |
| Search for a phrase                | Documents containing the phrase are returned                                 |
| Search for an absent word          | A clear no-results message appears                                           |
| Search an empty query              | The system asks for a search term                                            |
| Upload an unsupported file         | The system displays an error                                                 |
| Upload an empty document           | The system handles it without crashing                                       |
| Search after adding a document     | The new document can be found                                                |
| Search using related meanings      | Semantic search retrieves relevant results after that feature is implemented |

---

## 13. Security and Privacy Considerations

RecallQ is intended to search personal documents, so file handling and privacy are important.

* Validate file types and sizes before processing.
* Use parameterized SQL queries.
* Keep database credentials and secrets in environment variables.
* Do not upload personal documents or credentials to the public repository.
* Keep the local upload directory out of Git.
* Handle malformed files and extraction failures safely.
* Restrict access to uploaded files and prevent unsafe file paths.
* Use test documents during development.
* If deployment or multi-user access is introduced, implement appropriate authentication, authorization, and file isolation.

These protections will be implemented and tested as the project develops.

---

## 14. Expected Outcome

The expected outcome is a working web application that allows users to locate personal documents by searching the information contained inside them.

The application will initially demonstrate keyword-based search with clear explanations. Later versions will support more document formats, database storage, and semantic search.

The project will also demonstrate practical skills in React, Flask, Python, MySQL, REST APIs, Git, GitHub collaboration, document processing, and software testing.

---

## 15. Current Project Status

* [x] GitHub repository created.
* [x] Team collaborators invited.
* [x] Git installed and configured for the initial developer.
* [x] Local branches created and basic Git workflow practised.
* [x] Initial project README prepared.
* [ ] All teammates have cloned the repository.
* [ ] All teammates have verified their branches and pull-request workflow.
* [ ] Frontend and backend skeletons created.
* [ ] Basic TXT keyword search implemented.
* [ ] Document extraction implemented.
* [ ] MySQL integration completed.
* [ ] React and Flask integration completed.
* [ ] Semantic search implemented and tested.
* [ ] Final testing and documentation completed.

*The checklist reflects planned work and should be updated as tasks are actually completed.*

---

## 16. Conclusion

RecallQ aims to make personal document retrieval easier by helping users search for information they remember instead of relying only on filenames or folder locations.

The team will develop the project incrementally, maintain shared code through GitHub, test every milestone, and document the implementation as the system evolves.
