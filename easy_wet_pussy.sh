#!/bin/bash
# Autonomous Git Remediation Sequence (AGRS)
# Fixes malformed remote URLs and non-fast-forward rejects in a single, safe execution.

# --- Configuration Variables (REPLACE THESE) ---
# IMPORTANT: Replace these placeholders with your actual values.
# Use your GitHub token (GH_TOKEN) instead of a password for security.
GITHUB_USERNAME="mrmsoc09"
REPO_NAME="WilsonsRaider-ChimeraEdition"
DEFAULT_BRANCH="master"
GH_TOKEN="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" # Optional: Use if you embed token in URL (less secure than credential helper)
NEW_REMOTE_URL="https://${GITHUB_USERNAME}@github.com/${GITHUB_USERNAME}/${REPO_NAME}.git"

# --- 1. INSPECT AND DISPLAY CURRENT STATE ---
echo "--- 1. INSPECTING CURRENT GIT REMOTES ---"
git remote -v
echo ""

# --- 2. RECONFIGURE AND AUTHENTICATE REMOTE URL ---
echo "--- 2. RECONFIGURING REMOTE URL FOR AUTHENTICATION ---"

# We use 'set-url' if 'origin' exists, otherwise 'add' (less destructive than 'remove' and 'add')
if git remote get-url origin > /dev/null 2>&1; then
    echo "Remote 'origin' found. Setting new URL: ${NEW_REMOTE_URL}"
    # Using HTTPS protocol for simplicity; this will prompt for credentials or use a helper.
    # If you prefer to embed the token (less secure but non-interactive):
    # git remote set-url origin "https://${GITHUB_USERNAME}:${GH_TOKEN}@github.com/${GITHUB_USERNAME}/${REPO_NAME}.git"
    git remote set-url origin "${NEW_REMOTE_URL}"
else
    echo "Remote 'origin' not found. Adding new remote."
    git remote add origin "${NEW_REMOTE_URL}"
fi
echo "New remote configuration:"
git remote -v
echo ""

# --- 3. CONFIGURE GIT IDENTITY (if necessary) ---
echo "--- 3. VERIFYING GIT IDENTITY ---"
if [ -z "$(git config user.email)" ]; then
    echo "Warning: Git user.email not set. Setting default identity."
    git config user.name "AgentZero"
    git config user.email "agent0@localhost"
fi
echo "Current identity: $(git config user.name) <$(git config user.email)>"
echo ""

# --- 4. SYNCHRONIZE AND REBASE TO RESOLVE NON-FAST-FORWARD ---
echo "--- 4. SYNCHRONIZING AND REBASING FOR NON-FAST-FORWARD FIX ---"
echo "Fetching latest changes from origin..."
git fetch origin

# Attempt to pull and rebase the local branch onto the remote branch
echo "Attempting 'git pull --rebase origin ${DEFAULT_BRANCH}'..."
# '|| true' allows the script to continue if the rebase results in conflicts
git pull --rebase origin "${DEFAULT_BRANCH}" || {
    echo "--- REBASE CONFLICTS DETECTED ---"
    echo "Manual intervention required: Resolve conflicts, then run 'git rebase --continue'."
    exit 1
}
echo "Synchronization complete."
echo ""

# --- 5. PUSH THE BRANCH ---
echo "--- 5. FINAL PUSH TO ORIGIN ---"
echo "Executing 'git push -u origin ${DEFAULT_BRANCH}'..."
git push -u origin "${DEFAULT_BRANCH}"

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ SUCCESS: Push completed. Agent-Zero's configuration is live."
else
    echo ""
    echo "❌ FAILURE: Git push failed. Please check credentials or review the output for conflicts."
fi

# Cleanup (optional, but good practice if using token embedding)
# if [ ! -z "${GH_TOKEN}" ]; then
#     # Prompt or mechanism to remove token from history if necessary
#     :
# fi
