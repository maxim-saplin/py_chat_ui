import streamlit_authenticator_2 as stauth
import yaml
import sys
import argparse


# Function to create a user entry for the YAML file
def create_user_entry(username, password):
    hashed_pw = stauth.Hasher([password]).generate()[0]
    user_entry = {
        username: {
            'email': f'{username}@example.com',  # Placeholder email
            'name': username.capitalize(),      # Capitalize the username for the name
            'password': hashed_pw               # Hashed password
        }
    }
    return user_entry


# Function to print the user entry for manual insertion into the YAML file
def print_user_entry(username, password):
    user_entry = create_user_entry(username, password)
    print(yaml.dump(user_entry, default_flow_style=False))
    return f"User entry for {username} printed. Please insert it manually into the YAML file."


# Command line argument parser
def parse_arguments():
    parser = argparse.ArgumentParser(
        description='Command line tool to print a user entry for manual insertion into the YAML file.')
    parser.add_argument('-u', '--username', type=str, help='Username for the new user')
    parser.add_argument('-p', '--password', type=str, help='Password for the new user')
    return parser.parse_args()


# Main function
def main():
    args = parse_arguments()

    if not args.username or not args.password:
        print('Usage: python generate_pass.py --username <username> --password <password>')
        sys.exit(1)

    result = print_user_entry(args.username, args.password)
    print(result)


# Entry point
if __name__ == '__main__':
    main()
