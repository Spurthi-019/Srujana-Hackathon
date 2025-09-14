#!/usr/bin/env node

/**
 * Auto-commit script for ClassTrack project
 * Automatically commits and pushes changes after every 3-4 file modifications
 */

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

class AutoCommitter {
  constructor() {
    this.changeCount = 0;
    this.lastCommitTime = Date.now();
    this.trackedFiles = [
      'src/**/*.{ts,tsx,js,jsx}',
      '*.{ts,tsx,js,jsx,json,md}',
      '.env',
      '.env.example',
      'detect/**/*.py'
    ];
    this.commitThreshold = 3; // Number of changes before auto-commit
    this.timeThreshold = 5 * 60 * 1000; // 5 minutes in milliseconds
  }

  // Check if git repository has changes
  hasChanges() {
    try {
      const status = execSync('git status --porcelain', { encoding: 'utf8' });
      return status.trim().length > 0;
    } catch (error) {
      console.error('Error checking git status:', error.message);
      return false;
    }
  }

  // Get list of changed files
  getChangedFiles() {
    try {
      const status = execSync('git status --porcelain', { encoding: 'utf8' });
      return status.trim().split('\n').filter(line => line.length > 0);
    } catch (error) {
      console.error('Error getting changed files:', error.message);
      return [];
    }
  }

  // Generate commit message based on changes
  generateCommitMessage(changedFiles) {
    const changes = changedFiles.map(line => {
      const status = line.substring(0, 2);
      const file = line.substring(3);
      return { status: status.trim(), file };
    });

    // Categorize changes
    const categories = {
      feat: [],
      fix: [],
      style: [],
      refactor: [],
      docs: [],
      config: []
    };

    changes.forEach(({ status, file }) => {
      if (file.includes('.md')) {
        categories.docs.push(file);
      } else if (file.includes('.env') || file.includes('config')) {
        categories.config.push(file);
      } else if (file.includes('.css') || file.includes('.scss')) {
        categories.style.push(file);
      } else if (status === 'A') {
        categories.feat.push(file);
      } else if (status === 'M') {
        categories.fix.push(file);
      } else {
        categories.refactor.push(file);
      }
    });

    // Generate message
    let message = '';
    let type = 'chore';

    if (categories.feat.length > 0) {
      type = 'feat';
      message = `Add new features and components`;
    } else if (categories.fix.length > 0) {
      type = 'fix';
      message = `Update and improve existing functionality`;
    } else if (categories.style.length > 0) {
      type = 'style';
      message = `Update styling and UI components`;
    } else if (categories.config.length > 0) {
      type = 'config';
      message = `Update configuration files`;
    } else {
      message = `Auto-commit: various improvements`;
    }

    const timestamp = new Date().toLocaleString();
    return `${type}: ${message}\n\n- Auto-committed on ${timestamp}\n- Files changed: ${changes.length}`;
  }

  // Perform auto-commit
  async autoCommit() {
    try {
      if (!this.hasChanges()) {
        console.log('📝 No changes to commit');
        return false;
      }

      const changedFiles = this.getChangedFiles();
      console.log(`📋 Found ${changedFiles.length} changed files`);

      // Add all changes
      execSync('git add .', { stdio: 'inherit' });

      // Generate and execute commit
      const commitMessage = this.generateCommitMessage(changedFiles);
      execSync(`git commit -m "${commitMessage}"`, { stdio: 'inherit' });

      // Push to remote
      const currentBranch = execSync('git rev-parse --abbrev-ref HEAD', { encoding: 'utf8' }).trim();
      execSync(`git push origin ${currentBranch}`, { stdio: 'inherit' });

      console.log('✅ Auto-commit and push completed successfully!');
      console.log(`🔄 Committed ${changedFiles.length} changes to ${currentBranch}`);
      
      this.changeCount = 0;
      this.lastCommitTime = Date.now();
      return true;

    } catch (error) {
      console.error('❌ Auto-commit failed:', error.message);
      return false;
    }
  }

  // Check if should auto-commit based on thresholds
  shouldAutoCommit() {
    const changedFiles = this.getChangedFiles();
    const timeSinceLastCommit = Date.now() - this.lastCommitTime;

    // Auto-commit if we have enough changes OR enough time has passed
    return changedFiles.length >= this.commitThreshold || 
           (changedFiles.length > 0 && timeSinceLastCommit > this.timeThreshold);
  }

  // Start monitoring for changes
  startMonitoring() {
    console.log('🚀 Starting auto-commit monitoring...');
    console.log(`📊 Will auto-commit after ${this.commitThreshold} changes or 5 minutes`);
    
    setInterval(async () => {
      if (this.shouldAutoCommit()) {
        console.log('🔄 Auto-commit threshold reached, committing changes...');
        await this.autoCommit();
      }
    }, 30000); // Check every 30 seconds
  }

  // Manual commit trigger
  async manualCommit() {
    console.log('🔄 Triggering manual commit...');
    return await this.autoCommit();
  }
}

// CLI interface
if (require.main === module) {
  const autoCommitter = new AutoCommitter();
  
  const args = process.argv.slice(2);
  if (args.includes('--start') || args.includes('-s')) {
    autoCommitter.startMonitoring();
  } else if (args.includes('--commit') || args.includes('-c')) {
    autoCommitter.manualCommit().then(success => {
      process.exit(success ? 0 : 1);
    });
  } else {
    console.log(`
🔧 ClassTrack Auto-Commit Tool

Usage:
  node auto-commit.js --start    Start monitoring for auto-commits
  node auto-commit.js --commit   Manually trigger a commit
  
Options:
  -s, --start     Start background monitoring
  -c, --commit    Manual commit now
  
The tool will automatically commit and push changes after:
- 3 or more files are modified, OR
- 5 minutes have passed with pending changes
    `);
  }
}

module.exports = AutoCommitter;