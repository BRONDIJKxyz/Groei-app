
# test push 2

# 🧠 Git Cheat Sheet for Groei App

This is your quick reference for working together on the Groei App using Git and GitHub.

---

## 🚀 Basic Workflow

### 1. Make sure you're on the main branch and up to date
```bash
git checkout main
git pull origin main
```

### 2. Create a new feature branch
```bash
git checkout -b feature/your-feature-name
```

### 3. Work on your feature, then stage and commit
```bash
git add .
git commit -m "Add: short description of what you did"
```

### 4. Push your feature branch to GitHub
```bash
git push origin feature/your-feature-name
```

### 5. Open a Pull Request
Go to GitHub → Pull Requests → New Pull Request  
Base: `main` ← Compare: `feature/your-feature-name`

---

## 🔁 After a PR is Merged

### 6. Pull the latest changes to your local main
```bash
git checkout main
git pull origin main
```

---

## 🧼 Extra Tips

- Use short, clear branch names: `feature/login-form`, `bug/fix-navbar`, etc.
- Always pull before starting new work
- Never commit directly to `main`

---

Happy coding! 💪
