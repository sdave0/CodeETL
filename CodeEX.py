import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QFileDialog, 
                             QVBoxLayout, QHBoxLayout, QWidget, QListWidget, 
                             QLabel, QMessageBox, QTextEdit)
from PyQt5.QtCore import Qt

class CodeFileCollector(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Code File Collector")
        self.setGeometry(100, 100, 800, 600)
        
        # Store selected file paths
        self.selected_files = []
        
        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        
        # Create file selection area
        file_selection_layout = QHBoxLayout()
        
        # Create buttons for file operations
        button_layout = QVBoxLayout()
        self.add_files_btn = QPushButton("Add Files")
        self.add_files_btn.clicked.connect(self.add_files)
        self.add_folder_btn = QPushButton("Add Folder Structure")
        self.add_folder_btn.clicked.connect(self.add_folder_structure)
        self.remove_file_btn = QPushButton("Remove Selected")
        self.remove_file_btn.clicked.connect(self.remove_selected_file)
        self.clear_all_btn = QPushButton("Clear All")
        self.clear_all_btn.clicked.connect(self.clear_all_files)
        
        button_layout.addWidget(self.add_files_btn)
        button_layout.addWidget(self.add_folder_btn)  # Added new button
        button_layout.addWidget(self.remove_file_btn)
        button_layout.addWidget(self.clear_all_btn)
        button_layout.addStretch()
        
        # Create list for displaying selected files
        list_layout = QVBoxLayout()
        list_label = QLabel("Selected Files:")
        self.file_list = QListWidget()
        self.file_list.setSelectionMode(QListWidget.SingleSelection)
        
        list_layout.addWidget(list_label)
        list_layout.addWidget(self.file_list)
        
        file_selection_layout.addLayout(button_layout, 1)
        file_selection_layout.addLayout(list_layout, 3)
        
        # Create preview area
        preview_label = QLabel("Preview:")
        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        
        # Create export button
        self.export_btn = QPushButton("Export to Text File")
        self.export_btn.clicked.connect(self.export_to_file)
        
        # Add all components to main layout
        main_layout.addLayout(file_selection_layout)
        main_layout.addWidget(preview_label)
        main_layout.addWidget(self.preview_text)
        main_layout.addWidget(self.export_btn)
    
    def add_files(self):
        """Open file dialog to select multiple code files"""
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.ExistingFiles)
        file_dialog.setNameFilter("Code Files (*.py *.js *.html *.css *.ts *.tsx *.jsx *.c *.cpp *.h *.java *.php *.rb *.go *.rs *.swift)")
        
        if file_dialog.exec_():
            new_files = file_dialog.selectedFiles()
            for file_path in new_files:
                if file_path not in self.selected_files:
                    self.selected_files.append(file_path)
                    # Add to list widget
                    self.file_list.addItem(file_path)
            
            self.update_preview()
    
    def add_folder_structure(self):
        """Open folder dialog and add folder structure to the preview"""
        folder_path = QFileDialog.getExistingDirectory(self, "Select Folder")
        
        if folder_path:
            # Create a virtual file to represent the folder structure
            structure_name = f"FOLDER_STRUCTURE: {os.path.basename(folder_path)}"
            
            # Add to the list if not already there
            if structure_name not in self.selected_files:
                self.selected_files.append(structure_name)
                self.file_list.addItem(structure_name)
                
                # Generate folder structure content
                folder_content = self.generate_folder_structure(folder_path)
                
                # Store the structure content in a temporary file
                temp_path = os.path.join(os.path.dirname(folder_path), f".{os.path.basename(folder_path)}_structure.txt")
                with open(temp_path, 'w', encoding='utf-8') as temp_file:
                    temp_file.write(folder_content)
                
                # Replace the structure name in the list with the temp file path
                index = self.selected_files.index(structure_name)
                self.selected_files[index] = temp_path
                
                self.update_preview()
    
    def generate_folder_structure(self, folder_path):
        """Generate a text representation of the folder structure"""
        structure_content = f"Folder Structure: {folder_path}\n"
        structure_content += "=" * 50 + "\n\n"
        
        for root, dirs, files in os.walk(folder_path):
            # Calculate the relative path from the base folder
            level = root.replace(folder_path, '').count(os.sep)
            indent = '│   ' * level
            structure_content += f"{indent}├── {os.path.basename(root)}/\n"
            
            # Add files
            sub_indent = '│   ' * (level + 1)
            for file in sorted(files):
                file_path = os.path.join(root, file)
                file_size = os.path.getsize(file_path)
                size_str = self.format_file_size(file_size)
                structure_content += f"{sub_indent}├── {file} ({size_str})\n"
                
        return structure_content
    
    def format_file_size(self, size_in_bytes):
        """Format file size in a human-readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_in_bytes < 1024.0:
                return f"{size_in_bytes:.2f} {unit}"
            size_in_bytes /= 1024.0
        return f"{size_in_bytes:.2f} TB"
    
    def remove_selected_file(self):
        """Remove the selected file from the list"""
        selected_items = self.file_list.selectedItems()
        if not selected_items:
            return
            
        for item in selected_items:
            row = self.file_list.row(item)
            removed_file = item.text()
            self.file_list.takeItem(row)
            
            # Find the actual path in the selected_files list
            for file_path in self.selected_files:
                if removed_file in file_path or file_path in removed_file:
                    self.selected_files.remove(file_path)
                    break
        
        self.update_preview()
    
    def clear_all_files(self):
        """Clear all files from the list"""
        self.file_list.clear()
        self.selected_files = []
        self.update_preview()
    
    def update_preview(self):
        """Update the preview text area with the combined content"""
        if not self.selected_files:
            self.preview_text.setText("No files selected.")
            return
            
        preview = self.generate_combined_content(max_lines=10)
        self.preview_text.setText(preview)
    
    def generate_combined_content(self, max_lines=None):
        """Generate the combined content from all selected files"""
        combined_content = ""
        
        for file_path in self.selected_files:
            try:
                is_folder_structure = "FOLDER_STRUCTURE" in file_path or "_structure.txt" in file_path
                display_name = file_path
                
                if is_folder_structure:
                    display_name = "FOLDER STRUCTURE: " + os.path.basename(os.path.dirname(file_path))
                
                combined_content += f"{display_name}\n"
                
                with open(file_path, 'r', encoding='utf-8') as file:
                    lines = file.readlines()
                    
                    # For folder structures, don't limit the preview
                    if max_lines and not is_folder_structure and len(lines) > max_lines:
                        content = ''.join(lines[:max_lines]) + f"\n... ({len(lines) - max_lines} more lines) ...\n"
                    else:
                        content = ''.join(lines)
                    
                    combined_content += content + "\n\n"
            except Exception as e:
                combined_content += f"Error reading file: {str(e)}\n\n"
        
        return combined_content
    
    def export_to_file(self):
        """Export the combined content to a text file"""
        if not self.selected_files:
            QMessageBox.warning(self, "Warning", "No files selected to export.")
            return
            
        # Open save file dialog
        save_path, _ = QFileDialog.getSaveFileName(
            self, "Save Combined Code", "", "Text Files (*.txt)"
        )
        
        if not save_path:
            return  # User canceled
            
        try:
            # Generate the full content without preview limits
            full_content = self.generate_combined_content(max_lines=None)
            
            # Write to file
            with open(save_path, 'w', encoding='utf-8') as output_file:
                output_file.write(full_content)
                
            QMessageBox.information(self, "Success", f"Combined code exported to:\n{save_path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to export: {str(e)}")

def main():
    app = QApplication(sys.argv)
    window = CodeFileCollector()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()