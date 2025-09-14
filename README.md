# ClassTrack - Student & Faculty Management System# Getting Started with Create React App



A comprehensive web application for managing student and faculty records with speech recognition capabilities. Built with **FastAPI** backend, **React TypeScript** frontend, and **MongoDB** database.This project was bootstrapped with [Create React App](https://github.com/facebook/create-react-app).



## 🚀 Quick Start## Available Scripts



### PrerequisitesIn the project directory, you can run:

- Python 3.8+

- Node.js 16+### `npm start`

- MongoDB running on localhost:27017

- GitRuns the app in the development mode.\

Open [http://localhost:3000](http://localhost:3000) to view it in the browser.

### Backend Setup (FastAPI)

```bashThe page will reload if you make edits.\

cd detectYou will also see any lint errors in the console.

pip install -r requirements.txt

python main.py### `npm test`

```

Server runs on: `http://localhost:5001`Launches the test runner in the interactive watch mode.\

See the section about [running tests](https://facebook.github.io/create-react-app/docs/running-tests) for more information.

### Frontend Setup (React)

```bash### `npm run build`

npm install

npm startBuilds the app for production to the `build` folder.\

```It correctly bundles React in production mode and optimizes the build for the best performance.

Application runs on: `http://localhost:3000`

The build is minified and the filenames include the hashes.\

## 📦 Project StructureYour app is ready to be deployed!



```See the section about [deployment](https://facebook.github.io/create-react-app/docs/deployment) for more information.

srujana-hackathon/

├── detect/               # FastAPI Backend### `npm run eject`

│   ├── main.py          # Main FastAPI server

│   └── requirements.txt # Python dependencies**Note: this is a one-way operation. Once you `eject`, you can’t go back!**

├── src/                 # React Frontend

│   ├── components/      # React componentsIf you aren’t satisfied with the build tool and configuration choices, you can `eject` at any time. This command will remove the single build dependency from your project.

│   ├── services/        # API services

│   └── ...Instead, it will copy all the configuration files and the transitive dependencies (webpack, Babel, ESLint, etc) right into your project so you have full control over them. All of the commands except `eject` will still work, but they will point to the copied scripts so you can tweak them. At this point you’re on your own.

├── .env                 # Environment variables

├── package.json         # Node.js configurationYou don’t have to ever use `eject`. The curated feature set is suitable for small and middle deployments, and you shouldn’t feel obligated to use this feature. However we understand that this tool wouldn’t be useful if you couldn’t customize it when you are ready for it.

└── auto-commit.*        # Auto-commit scripts

```## Learn More



## 🤖 Auto-Commit SystemYou can learn more in the [Create React App documentation](https://facebook.github.io/create-react-app/docs/getting-started).



This project includes an automated git workflow system that commits and pushes changes after accumulating 3-4 modifications.To learn React, check out the [React documentation](https://reactjs.org/).


### Usage Options

#### 1. NPM Scripts (Recommended)
```bash
# Manual commit with current changes
npm run auto-commit

# Start monitoring mode (commits every 3+ changes)
npm run auto-commit-start

# Quick push (PowerShell script)
npm run git-push
```

#### 2. Direct PowerShell Execution
```bash
# Default behavior (3+ changes required)
./auto-commit.ps1

# Force commit regardless of change count
./auto-commit.ps1 -Force

# Custom minimum change threshold
./auto-commit.ps1 -MinChanges 5
```

#### 3. Node.js Monitoring Script
```bash
# Continuous monitoring with intelligent commits
node auto-commit.js
```

### Features
- **Smart Change Detection**: Categorizes files by type (Frontend, Backend, Config, etc.)
- **Intelligent Commit Messages**: Auto-generates descriptive commit messages
- **Threshold-Based Commits**: Configurable minimum change count
- **Multi-Platform Support**: PowerShell, Node.js, and Batch scripts
- **Cross-Platform Compatible**: Works on Windows, macOS, and Linux

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the project root:
```env
MONGODB_URI=mongodb://localhost:27017
REACT_APP_API_URL=http://localhost:5001
REACT_APP_CLERK_PUBLISHABLE_KEY=your_clerk_key_here
```

### Auto-Commit Settings
- **Default minimum changes**: 3 files
- **Supported file types**: .js, .ts, .py, .json, .css, .md, etc.
- **Commit categories**: Frontend, Backend, Config, Docs, Styling

## 🛠 Development

### Running Both Servers
```bash
# Terminal 1 - Backend
cd detect && python main.py

# Terminal 2 - Frontend  
npm start

# Terminal 3 - Auto-commit (optional)
npm run auto-commit-start
```

### API Endpoints
- `GET /students` - List all students
- `POST /students` - Add new student
- `GET /faculty` - List all faculty
- `POST /faculty` - Add new faculty
- `POST /speech/recognize` - Speech recognition
- `GET /speech/status` - Speech service status

## 📝 Git Workflow

The auto-commit system helps maintain a clean git history:

1. **Automatic Detection**: Monitors file changes in real-time
2. **Smart Categorization**: Groups changes by file type and purpose
3. **Descriptive Messages**: Generates commit messages like:
   - "Update Frontend files (3 modified, 1 added)"
   - "Add Backend files (2 added)"
   - "Update Config files (1 modified)"
4. **Automated Push**: Pushes to current branch after each commit

## 🧪 Testing

### Manual Testing
1. Make changes to 3+ files
2. Run `npm run auto-commit`
3. Verify commit and push in GitHub

### Continuous Monitoring
1. Run `npm run auto-commit-start`
2. Make changes to files
3. Script automatically commits after threshold

## 📊 Features

- **Student Management**: Add, view, and manage student records
- **Faculty Management**: Add, view, and manage faculty records  
- **Speech Recognition**: Voice-to-text capabilities for data entry
- **MongoDB Integration**: Persistent data storage
- **Real-time Updates**: Live data synchronization
- **Responsive Design**: Mobile-friendly interface

## 🔄 Migration Notes

This project was migrated from:
- **Flask** → **FastAPI** (better async support)
- **Firebase** → **MongoDB** (local development)
- **Port 5000** → **Port 5001** (conflict resolution)

## 📚 Dependencies

### Backend (Python)
- FastAPI
- Motor (async MongoDB driver)
- SpeechRecognition
- CORS middleware

### Frontend (Node.js)
- React 18
- TypeScript
- Clerk (authentication)
- Axios (HTTP client)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes (auto-commit will track them)
4. Submit a pull request

The auto-commit system will help maintain clean commit history during development!

---

## Create React App Documentation

This project was bootstrapped with [Create React App](https://github.com/facebook/create-react-app).

### Available Scripts

#### `npm start`
Runs the app in development mode. Open [http://localhost:3000](http://localhost:3000) to view it in the browser.

#### `npm test`
Launches the test runner in interactive watch mode.

#### `npm run build`
Builds the app for production to the `build` folder.

#### `npm run eject`
**Note: this is a one-way operation. Once you `eject`, you can't go back!**

## Learn More

You can learn more in the [Create React App documentation](https://facebook.github.io/create-react-app/docs/getting-started).

To learn React, check out the [React documentation](https://reactjs.org/).