# RecallQ — Intelligent Personal File Retrieval System

## 1. Project Description

RecallQ is an intelligent personal file retrieval system that helps users find their documents when they cannot remember the exact file name, folder location, or keywords used in the document.

Users will be able to search using natural-language queries, including simple English or Hindi queries. RecallQ will analyze the search query and available document information to identify relevant files and explain why each result matches the query.

For example, a user may search:
"Find the Infosys placement eligibility PDF that mentions 60% marks."

RecallQ will try to identify the relevant document and display the matching file location and the reasons it was retrieved.

## 2. Problem Statement

People store many documents, including PDFs, notes, assignments, resumes, placement notices, and certificates, across different folders on their computers.

Finding a particular document becomes difficult when the user:
- Forgets the exact file name.
- Cannot remember the folder in which the file was saved.
- Remembers the meaning of the document but not its exact wording.
- Has multiple documents with similar names or content.

Traditional file search often depends on file names or exact keywords. RecallQ aims to make document retrieval easier by allowing users to describe what they remember about a file.

## 3. Project Objectives

- Allow users to search for documents using natural-language queries.
- Help retrieve relevant files even when their exact names are unknown.
- Extract searchable text from supported document formats, especially PDF and TXT.
- Match queries with document content and metadata.
- Display relevant results with file names, locations, and matching reasons.
- Support common English queries and explore Hindi query support.
- Provide a simple, user-friendly interface.
- Keep the system focused on personal document retrieval.

## 4. Proposed Features

### Core Features
1. Document indexing for supported files.
2. Text extraction from supported documents.
3. Natural-language search.
4. Content-based document matching.
5. Ranked search results.
6. Explainable results showing why a document matched.
7. File name and location display.
8. A simple search interface.

### Planned Enhancements
- Hindi and multilingual search support.
- Filters by file type or folder.
- Improved relevance ranking.

Planned enhancements will be implemented if time and project scope permit.

## 5. Proposed Technology Stack

| Component | Technology | Purpose |
|---|---|---|
| Frontend | React.js | Search interface and results display |
| Styling | HTML, CSS, Bootstrap | Responsive user interface |
| Backend | Python, Flask | API and application logic |
| Text Processing | Python libraries | Extract and process document text |
| Search and Ranking | TF-IDF and cosine similarity | Find and rank relevant documents |
| Database | SQLite (initial proposal) | Store document metadata and index information |
| API Communication | REST API | Connect frontend and backend |
| Version Control | Git and GitHub | Team collaboration and code management |
| Development Tools | VS Code, Postman | Development and API testing |

Note: This is the proposed stack. Final choices may be adjusted after the team reviews the requirements. TF-IDF and cosine similarity are planned as the initial search approach; they do not provide full semantic understanding by themselves.

## 6. System Workflow

1. The user selects or specifies a folder containing documents.
2. The backend scans supported files.
3. Text is extracted from readable documents.
4. The system processes the extracted text and creates a searchable index.
5. The user enters a natural-language query.
6. The backend compares the query with indexed document content.
7. Matching documents are ranked by relevance.
8. The interface displays the results, file locations, and matching reasons.

## 7. Team Members and Responsibilities

Update the placeholders below with the actual team members and GitHub usernames.

| Team Member | Assigned Module | Responsibilities |
|---|---|---|
| Payal Kumari | Backend and Search Logic | Help develop Flask APIs, search processing, relevance ranking, and result explanations. |
| Member 2: [Name] | Frontend | Develop the React search page, result cards, and user interface. |
| Member 3: [Name] | Document Processing | Work on folder scanning, supported file formats, text extraction, and indexing. |
| Member 4: [Name] | Database and Testing | Help design metadata storage, test search scenarios, document bugs, and prepare test cases. |

All members will review each other's code, participate in integration, update project documentation, and test the final system. Responsibilities can be adjusted by mutual agreement.

## 8. Initial Folder Structure

```text
RecallQ/
├── frontend/
├── backend/
├── docs/
├── README.md
└── .gitignore
```

- frontend/: React application (created during implementation).
- backend/: Flask application and search logic.
- docs/: Project proposal, workflow, diagrams, and testing documents.
- README.md: Project overview, setup instructions, and team responsibilities.
- .gitignore: Files and folders Git should not track.

## 9. Installation and Setup

### Prerequisites
Install the following tools before starting implementation:
- Python 3.11 or another version agreed upon by the team.
- Node.js LTS and npm.
- Git.
- Visual Studio Code.
- A GitHub account and access to the shared repository.

Verify installations using:

```bash
git --version
python --version
node --version
npm --version
```

On Windows, if `python --version` does not work, try `py --version`.

### Clone the Repository

If the repository has not already been cloned:

```bash
git clone <YOUR-GITHUB-REPOSITORY-URL>
cd RecallQ
```

If RecallQ is already open in VS Code and connected to the correct repository, do not clone it again.

### Installation Status

No application dependencies are required at the planning stage. The Python virtual environment, Flask packages, React dependencies, and other libraries will be installed after the team finalizes the structure and begins implementation.

Detailed setup commands will be added here when the application is ready to run.

## 10. Team Git Workflow

1. Pull the latest changes from `main` before starting new work.
2. Create or switch to your assigned branch.
3. Work only on your assigned files and module.
4. Check changes using `git status`.
5. Stage and commit your changes with a meaningful message.
6. Push your branch to GitHub.
7. Open a pull request into `main`.
8. Review and test changes before merging.
9. Pull the updated `main` branch before continuing work.

Do not commit passwords, API keys, personal documents, virtual environments, or dependency folders.

## 11. Testing Plan

The team will test:
- Searching by an exact file name.
- Searching without knowing the file name.
- Searching for a phrase or topic mentioned inside a document.
- Finding a document using a remembered eligibility criterion.
- Handling empty queries and unsupported file types.
- Displaying correct file locations.
- Ranking relevant results above unrelated results.
- Explaining why each result was returned.
- Handling Hindi queries if multilingual support is implemented.

## 12. Limitations

- Search results depend on the quality of extracted document text.
- Scanned PDFs may require OCR, which can be added if needed.
- Initial keyword-based similarity may not understand every synonym or implied meaning.
- File access will depend on operating-system permissions and the folders selected by the user.
- Hindi and multilingual support will require additional processing and testing.

## 13. Expected Outcome

The expected outcome is a working prototype that allows users to retrieve personal documents by describing their content or purpose, even when they have forgotten the exact file name or storage location.

The system will aim to make document retrieval more convenient, relevant, and explainable.

## 14. Current Project Status

Phase 1: Planning and repository setup.

- [ ] Finalize project requirements.
- [ ] Confirm team members and responsibilities.
- [ ] Finalize the proposed technology stack.
- [ ] Complete README.md.
- [ ] Create the initial folder structure.
- [ ] Agree on Git branching and pull-request workflow.

Application development will begin after the planning and setup phase is complete.