"""
File management system with versioning and rollback capabilities.
"""

import os
import shutil
import json
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any
from git import Repo, GitCommandError
from .models import FileOperation, ProjectState, ConversationTurn


class FileManager:
    """Manages file operations with versioning and rollback capabilities."""
    
    def __init__(self, project_root: str, backup_dir: str = "./backups"):
        self.project_root = Path(project_root).resolve()
        self.backup_dir = Path(backup_dir).resolve()
        self.file_backups = {}
        
        # Ensure directories exist
        self.project_root.mkdir(parents=True, exist_ok=True)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize git repository if it doesn't exist
        self._init_git_repo()
    
    def _init_git_repo(self):
        """Initialize git repository for version control."""
        git_dir = self.project_root / ".git"
        if not git_dir.exists():
            try:
                self.repo = Repo.init(self.project_root)
                print(f"Initialized git repository at {self.project_root}")
            except GitCommandError as e:
                print(f"Warning: Could not initialize git repository: {e}")
                self.repo = None
        else:
            try:
                self.repo = Repo(self.project_root)
            except GitCommandError as e:
                print(f"Warning: Could not access git repository: {e}")
                self.repo = None
    
    def create_file(self, filepath: str, content: str) -> FileOperation:
        """
        Create a new file with content.
        
        Args:
            filepath: Path to the file to create
            content: Content to write to the file
            
        Returns:
            FileOperation object describing the operation
        """
        full_path = self.project_root / filepath
        
        # Create backup if file exists
        if full_path.exists():
            backup_path = self._create_backup(full_path)
        else:
            backup_path = None
        
        # Ensure parent directory exists
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write the file
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # Commit to git if available
        if self.repo:
            try:
                self.repo.index.add([str(full_path.relative_to(self.project_root))])
                self.repo.index.commit(f"Create file: {filepath}")
            except GitCommandError as e:
                print(f"Warning: Could not commit to git: {e}")
        
        operation = FileOperation(
            operation="create",
            filepath=str(full_path.relative_to(self.project_root)),
            content=content,
            backup_path=backup_path
        )
        
        return operation
    
    def modify_file(self, filepath: str, content: str) -> FileOperation:
        """
        Modify an existing file with new content.
        
        Args:
            filepath: Path to the file to modify
            content: New content for the file
            
        Returns:
            FileOperation object describing the operation
        """
        full_path = self.project_root / filepath
        
        if not full_path.exists():
            raise FileNotFoundError(f"File not found: {filepath}")
        
        # Create backup
        backup_path = self._create_backup(full_path)
        
        # Write the new content
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # Commit to git if available
        if self.repo:
            try:
                self.repo.index.add([str(full_path.relative_to(self.project_root))])
                self.repo.index.commit(f"Modify file: {filepath}")
            except GitCommandError as e:
                print(f"Warning: Could not commit to git: {e}")
        
        operation = FileOperation(
            operation="modify",
            filepath=str(full_path.relative_to(self.project_root)),
            content=content,
            backup_path=backup_path
        )
        
        return operation
    
    def delete_file(self, filepath: str) -> FileOperation:
        """
        Delete a file.
        
        Args:
            filepath: Path to the file to delete
            
        Returns:
            FileOperation object describing the operation
        """
        full_path = self.project_root / filepath
        
        if not full_path.exists():
            raise FileNotFoundError(f"File not found: {filepath}")
        
        # Create backup
        backup_path = self._create_backup(full_path)
        
        # Delete the file
        full_path.unlink()
        
        # Commit to git if available
        if self.repo:
            try:
                self.repo.index.remove([str(full_path.relative_to(self.project_root))])
                self.repo.index.commit(f"Delete file: {filepath}")
            except GitCommandError as e:
                print(f"Warning: Could not commit to git: {e}")
        
        operation = FileOperation(
            operation="delete",
            filepath=str(full_path.relative_to(self.project_root)),
            backup_path=backup_path
        )
        
        return operation
    
    def read_file(self, filepath: str) -> str:
        """
        Read content from a file.
        
        Args:
            filepath: Path to the file to read
            
        Returns:
            File content as string
        """
        full_path = self.project_root / filepath
        
        if not full_path.exists():
            raise FileNotFoundError(f"File not found: {filepath}")
        
        with open(full_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def list_files(self, pattern: str = "*") -> List[str]:
        """
        List files in the project directory.
        
        Args:
            pattern: Glob pattern to match files
            
        Returns:
            List of file paths relative to project root
        """
        files = []
        for file_path in self.project_root.rglob(pattern):
            if file_path.is_file():
                relative_path = file_path.relative_to(self.project_root)
                files.append(str(relative_path))
        
        return sorted(files)
    
    def search_in_files(self, query: str, file_pattern: str = "*.py") -> Dict[str, List[str]]:
        """
        Search for text in files.
        
        Args:
            query: Text to search for
            file_pattern: File pattern to search in
            
        Returns:
            Dictionary mapping file paths to list of matching lines
        """
        results = {}
        
        for file_path in self.project_root.rglob(file_pattern):
            if file_path.is_file():
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                    
                    matching_lines = []
                    for i, line in enumerate(lines, 1):
                        if query.lower() in line.lower():
                            matching_lines.append(f"{i}: {line.strip()}")
                    
                    if matching_lines:
                        relative_path = file_path.relative_to(self.project_root)
                        results[str(relative_path)] = matching_lines
                        
                except Exception as e:
                    print(f"Warning: Could not search in {file_path}: {e}")
        
        return results
    
    def _create_backup(self, file_path: Path) -> str:
        """Create a backup of a file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"{file_path.name}_{timestamp}.bak"
        backup_path = self.backup_dir / backup_filename
        
        # Copy the file
        shutil.copy2(file_path, backup_path)
        
        # Track backup
        relative_path = str(file_path.relative_to(self.project_root))
        if relative_path not in self.file_backups:
            self.file_backups[relative_path] = []
        self.file_backups[relative_path].append(str(backup_path))
        
        return str(backup_path)
    
    def rollback_file(self, filepath: str, backup_path: Optional[str] = None) -> FileOperation:
        """
        Rollback a file to a previous version.
        
        Args:
            filepath: Path to the file to rollback
            backup_path: Specific backup to restore (uses latest if None)
            
        Returns:
            FileOperation object describing the operation
        """
        full_path = self.project_root / filepath
        
        # Find backup to restore
        if backup_path is None:
            if filepath not in self.file_backups or not self.file_backups[filepath]:
                raise ValueError(f"No backups found for {filepath}")
            backup_path = self.file_backups[filepath][-1]  # Use latest backup
        
        backup_file = Path(backup_path)
        if not backup_file.exists():
            raise FileNotFoundError(f"Backup file not found: {backup_path}")
        
        # Create backup of current file if it exists
        current_backup = None
        if full_path.exists():
            current_backup = self._create_backup(full_path)
        
        # Restore from backup
        shutil.copy2(backup_file, full_path)
        
        # Commit to git if available
        if self.repo:
            try:
                self.repo.index.add([str(full_path.relative_to(self.project_root))])
                self.repo.index.commit(f"Rollback file: {filepath}")
            except GitCommandError as e:
                print(f"Warning: Could not commit to git: {e}")
        
        operation = FileOperation(
            operation="rollback",
            filepath=str(full_path.relative_to(self.project_root)),
            backup_path=current_backup
        )
        
        return operation
    
    def get_file_history(self, filepath: str) -> List[Dict[str, Any]]:
        """
        Get version history for a file.
        
        Args:
            filepath: Path to the file
            
        Returns:
            List of version information dictionaries
        """
        history = []
        
        # Get git history if available
        if self.repo:
            try:
                relative_path = str((self.project_root / filepath).relative_to(self.project_root))
                commits = list(self.repo.iter_commits(paths=relative_path))
                
                for commit in commits:
                    history.append({
                        "type": "git",
                        "hash": commit.hexsha[:8],
                        "message": commit.message.strip(),
                        "author": commit.author.name,
                        "date": commit.committed_datetime.isoformat(),
                        "timestamp": commit.committed_datetime.timestamp()
                    })
            except GitCommandError as e:
                print(f"Warning: Could not get git history: {e}")
        
        # Get backup history
        if filepath in self.file_backups:
            for backup_path in self.file_backups[filepath]:
                backup_file = Path(backup_path)
                if backup_file.exists():
                    stat = backup_file.stat()
                    history.append({
                        "type": "backup",
                        "path": backup_path,
                        "date": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                        "timestamp": stat.st_mtime
                    })
        
        # Sort by timestamp (newest first)
        history.sort(key=lambda x: x["timestamp"], reverse=True)
        
        return history
    
    def cleanup_old_backups(self, max_backups: int = 10):
        """Clean up old backup files, keeping only the most recent ones."""
        for filepath, backups in self.file_backups.items():
            if len(backups) > max_backups:
                # Sort by modification time
                backup_files = [(Path(b), Path(b).stat().st_mtime) for b in backups]
                backup_files.sort(key=lambda x: x[1], reverse=True)
                
                # Keep only the most recent backups
                backups_to_keep = [str(f[0]) for f in backup_files[:max_backups]]
                backups_to_remove = [str(f[0]) for f in backup_files[max_backups:]]
                
                # Update the backup list
                self.file_backups[filepath] = backups_to_keep
                
                # Remove old backup files
                for backup_path in backups_to_remove:
                    try:
                        Path(backup_path).unlink()
                    except Exception as e:
                        print(f"Warning: Could not remove backup {backup_path}: {e}")
    
    def get_project_state(self) -> ProjectState:
        """Get current project state."""
        active_files = self.list_files()
        
        return ProjectState(
            project_root=str(self.project_root),
            active_files=active_files,
            file_backups=self.file_backups
        )
