#!/usr/bin/env python3
"""
File Upload Script for Ritham Tours & Travels
This script uploads modified files to the server using various methods.
"""

import os
import sys
import paramiko
import getpass
from pathlib import Path
import argparse


class FileUploader:
    def __init__(self, host, username, password=None, key_file=None, port=22):
        self.host = host
        self.username = username
        self.password = password
        self.key_file = key_file
        self.port = port
        self.ssh = None
        self.sftp = None
    
    def connect(self):
        """Establish SSH connection"""
        try:
            self.ssh = paramiko.SSHClient()
            self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            if self.key_file:
                # Use SSH key authentication
                self.ssh.connect(
                    hostname=self.host,
                    port=self.port,
                    username=self.username,
                    key_filename=self.key_file
                )
            else:
                # Use password authentication
                if not self.password:
                    self.password = getpass.getpass(f"Password for {self.username}@{self.host}: ")
                
                self.ssh.connect(
                    hostname=self.host,
                    port=self.port,
                    username=self.username,
                    password=self.password
                )
            
            self.sftp = self.ssh.open_sftp()
            print(f"✅ Connected to {self.host}")
            return True
            
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return False
    
    def upload_file(self, local_path, remote_path):
        """Upload a single file"""
        try:
            # Create remote directory if it doesn't exist
            remote_dir = os.path.dirname(remote_path)
            try:
                self.sftp.makedirs(remote_dir)
            except:
                pass  # Directory might already exist
            
            self.sftp.put(local_path, remote_path)
            print(f"✅ Uploaded: {local_path} → {remote_path}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to upload {local_path}: {e}")
            return False
    
    def upload_files(self, file_mappings, remote_base_path="/var/www/ritham_tours"):
        """Upload multiple files"""
        success_count = 0
        total_count = len(file_mappings)
        
        print(f"\n📤 Uploading {total_count} files to {self.host}...")
        print("=" * 50)
        
        for local_file, remote_file in file_mappings.items():
            if not os.path.exists(local_file):
                print(f"⚠️  Local file not found: {local_file}")
                continue
            
            remote_path = f"{remote_base_path}/{remote_file}"
            if self.upload_file(local_file, remote_path):
                success_count += 1
        
        print("=" * 50)
        print(f"📊 Upload Summary: {success_count}/{total_count} files uploaded successfully")
        
        return success_count == total_count
    
    def execute_command(self, command):
        """Execute a command on the remote server"""
        try:
            stdin, stdout, stderr = self.ssh.exec_command(command)
            output = stdout.read().decode()
            error = stderr.read().decode()
            
            if output:
                print(f"📋 Command output:\n{output}")
            if error:
                print(f"⚠️  Command error:\n{error}")
            
            return output, error
            
        except Exception as e:
            print(f"❌ Command execution failed: {e}")
            return None, str(e)
    
    def restart_services(self):
        """Restart Django and web server services"""
        commands = [
            "sudo systemctl reload nginx",
            "sudo systemctl restart gunicorn",
            # Alternative commands if using different setup
            # "sudo service apache2 reload",
            # "sudo supervisorctl restart ritham_tours",
        ]
        
        print("\n🔄 Restarting services...")
        for command in commands:
            print(f"Executing: {command}")
            output, error = self.execute_command(command)
            if error and "not found" not in error.lower():
                print(f"⚠️  Service restart warning: {error}")
    
    def close(self):
        """Close connections"""
        if self.sftp:
            self.sftp.close()
        if self.ssh:
            self.ssh.close()
        print("🔌 Connection closed")


def get_modified_files():
    """Get list of files that were modified"""
    return {
        # Local file path : Remote file path
        "templates/tours/tour_info.html": "templates/tours/tour_info.html",
        "templates/bookings/online_cab_booking.html": "templates/bookings/online_cab_booking.html",
        "bookings/utils.py": "bookings/utils.py",
        "bookings/views.py": "bookings/views.py",
        "vehicles/management/commands/add_premium_vehicles.py": "vehicles/management/commands/add_premium_vehicles.py",
        "vehicles/management/__init__.py": "vehicles/management/__init__.py",
        "vehicles/management/commands/__init__.py": "vehicles/management/commands/__init__.py",
    }


def main():
    parser = argparse.ArgumentParser(description="Upload files to Ritham Tours server")
    parser.add_argument("--host", required=True, help="Server hostname or IP")
    parser.add_argument("--username", required=True, help="SSH username")
    parser.add_argument("--password", help="SSH password (will prompt if not provided)")
    parser.add_argument("--key-file", help="Path to SSH private key file")
    parser.add_argument("--port", type=int, default=22, help="SSH port (default: 22)")
    parser.add_argument("--remote-path", default="/var/www/ritham_tours", help="Remote base path")
    parser.add_argument("--no-restart", action="store_true", help="Skip service restart")
    
    args = parser.parse_args()
    
    # Get files to upload
    file_mappings = get_modified_files()
    
    print("🚀 Ritham Tours & Travels - File Upload Script")
    print("=" * 50)
    print(f"Target Server: {args.host}")
    print(f"Username: {args.username}")
    print(f"Remote Path: {args.remote_path}")
    print(f"Files to upload: {len(file_mappings)}")
    
    # Create uploader instance
    uploader = FileUploader(
        host=args.host,
        username=args.username,
        password=args.password,
        key_file=args.key_file,
        port=args.port
    )
    
    try:
        # Connect to server
        if not uploader.connect():
            sys.exit(1)
        
        # Upload files
        if uploader.upload_files(file_mappings, args.remote_path):
            print("✅ All files uploaded successfully!")
            
            # Run the management command to add vehicles
            print("\n🚗 Adding premium vehicles to database...")
            uploader.execute_command(f"cd {args.remote_path} && python manage.py add_premium_vehicles")
            
            # Restart services
            if not args.no_restart:
                uploader.restart_services()
            
            print("\n🎉 Deployment completed successfully!")
            
        else:
            print("❌ Some files failed to upload")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⏹️  Upload cancelled by user")
        sys.exit(1)
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)
        
    finally:
        uploader.close()


if __name__ == "__main__":
    # Check if paramiko is installed
    try:
        import paramiko
    except ImportError:
        print("❌ paramiko library is required. Install it with:")
        print("   pip install paramiko")
        sys.exit(1)
    
    main()