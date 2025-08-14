import logging
import os
from pathlib import Path
from typing import Optional, List

import reflex as rx
from ryoma_lab.models.vector_store import DocumentProject
from ryoma_lab.services.vector_store import VectorStoreService
from ryoma_lab.states.ai import AIState


class VectorStoreState(AIState):
    document_projects: List[DocumentProject] = []
    current_project: Optional[DocumentProject] = None

    # Project configuration
    project_name: str = ""
    project_description: str = ""

    # UI state
    create_project_dialog_open: bool = False
    upload_dialog_open: bool = False
    
    # File upload
    uploaded_files: List[str] = []

    # Dialog toggles
    def toggle_create_project_dialog(self):
        """Toggle the create project dialog."""
        self.create_project_dialog_open = not self.create_project_dialog_open

    def toggle_upload_dialog(self):
        """Toggle the upload dialog."""
        self.upload_dialog_open = not self.upload_dialog_open

    # Project management
    def set_project_name(self, name: str):
        """Set the project name."""
        self.project_name = name

    def set_project_description(self, description: str):
        """Set the project description."""
        self.project_description = description

    def get_project(self, project_name: str) -> Optional[DocumentProject]:
        """Get a project by name."""
        return next(
            (
                project
                for project in self.document_projects
                if project.project_name == project_name
            ),
            None,
        )

    def set_current_project(self, project_name: str):
        """Set the current project."""
        project = self.get_project(project_name)
        if project:
            self.current_project = project
            logging.info(f"Switched to project: {project_name}")

    def create_project(self):
        """Create a new document project."""
        if not self.project_name:
            logging.error("Project name is required")
            return

        try:
            with VectorStoreService() as service:
                project = service.create_project(
                    project_name=self.project_name,
                    description=self.project_description or None
                )
                self.document_projects.append(project)
                self.current_project = project
                logging.info(f"Created project: {self.project_name}")
                
                # Clear form
                self.project_name = ""
                self.project_description = ""
                
        except Exception as e:
            logging.error(f"Error creating project: {e}")
            raise e
        finally:
            self.toggle_create_project_dialog()

    def delete_project(self, project_name: str):
        """Delete a document project."""
        try:
            with VectorStoreService() as service:
                service.delete_project(project_name)
                
            # Remove from local list
            self.document_projects = [
                p for p in self.document_projects 
                if p.project_name != project_name
            ]
            
            # Clear current project if it was deleted
            if self.current_project and self.current_project.project_name == project_name:
                self.current_project = None
                
            logging.info(f"Deleted project: {project_name}")
            
        except Exception as e:
            logging.error(f"Error deleting project: {e}")
            raise e

    def load_projects(self):
        """Load all document projects."""
        try:
            with VectorStoreService() as service:
                self.document_projects = service.load_projects()
                
            # Set current project if none selected
            if not self.current_project and self.document_projects:
                self.current_project = self.document_projects[0]
                
            logging.info(f"Loaded {len(self.document_projects)} projects")
            
        except Exception as e:
            logging.error(f"Error loading projects: {e}")
            raise e

    def get_project_info(self, project_name: str) -> dict:
        """Get project information."""
        try:
            with VectorStoreService() as service:
                return service.get_project_info(project_name)
        except Exception as e:
            logging.error(f"Error getting project info: {e}")
            return {"error": str(e)}

    # File upload handling
    async def handle_upload(self, files: List[rx.UploadFile]):
        """Handle the upload of documents.

        Args:
            files: The uploaded files.
        """
        if not self.current_project:
            logging.error("No project selected for upload")
            return

        try:
            # Create upload directory
            root_dir = rx.get_upload_dir()
            project_dir = f"{root_dir}/{self.current_project.project_name}"
            if not os.path.exists(project_dir):
                os.makedirs(project_dir)

            file_paths = []
            for file in files:
                upload_data = await file.read()
                outfile = Path(f"{project_dir}/{file.filename}")

                # Save the file
                with outfile.open("wb") as file_object:
                    file_object.write(upload_data)

                file_paths.append(str(outfile))
                self.uploaded_files.append(file.filename)

            logging.info(f"Uploaded {len(file_paths)} files to project {self.current_project.project_name}")

        except Exception as e:
            logging.error(f"Error uploading files: {e}")
            raise e

    def index_uploaded_documents(self):
        """Index the uploaded documents using the selected embedding model."""
        if not self.current_project:
            logging.error("No project selected for indexing")
            return
            
        if not self.uploaded_files:
            logging.error("No files uploaded to index")
            return
            
        if not self.selected_model:
            logging.error("No embedding model selected")
            return

        try:
            # Get file paths for uploaded files
            root_dir = rx.get_upload_dir()
            project_dir = f"{root_dir}/{self.current_project.project_name}"
            file_paths = [f"{project_dir}/{filename}" for filename in self.uploaded_files]
            
            # Get embedding function from selected model
            embedding_function = self.get_embedding_function()
            
            with VectorStoreService() as service:
                total_chunks = service.index_documents(
                    project_name=self.current_project.project_name,
                    file_paths=file_paths,
                    embedding_function=embedding_function,
                    metadata={"indexed_at": str(rx.utils.format.utcnow())}
                )
                
                # Update document count
                project = service.get_project(self.current_project.project_name)
                if project:
                    project.document_count += len(file_paths)
                    service.session.commit()
                    
                    # Update local state
                    for i, p in enumerate(self.document_projects):
                        if p.project_name == self.current_project.project_name:
                            self.document_projects[i] = project
                            self.current_project = project
                            break
                
                logging.info(f"Successfully indexed {total_chunks} chunks from {len(file_paths)} files")
                
                # Clear uploaded files after successful indexing
                self.uploaded_files = []
                
        except Exception as e:
            logging.error(f"Error indexing documents: {e}")
            raise e

    def on_load(self) -> None:
        """Load projects when the page loads."""
        self.load_projects()
