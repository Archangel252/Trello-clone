# Kanban Web Application

This is a Kanban web application built using Flask, jQuery, Socket.IO, and Docker. The application allows users to create boards, lists, and cards, and drag and drop cards between lists with real-time updates for all users.

## Table of Contents
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
- [Docker Setup](#docker-setup)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

## Features
- User authentication (sign up and login)
- Create boards, lists, and cards
- Drag and drop cards between lists
- Real-time updates using Socket.IO
- Integrated chat functionality

## Prerequisites
- [Docker](https://www.docker.com/get-started)
- [Docker Compose](https://docs.docker.com/compose/install/)
- [Git](https://git-scm.com/)

## Installation
1. Clone the repository:
    ```sh
    git clone https://github.com/Archangel252/Trello-clone.git
    cd Trello-clone
    ```

2. Build and run the Docker container using Docker Compose:
    ```sh
    docker-compose up --build
    ```

## Usage
Once the application is running, you can access it at `http://localhost:8080`. Sign up for an account, create a board, add lists and cards, and start managing your tasks.

## Configuration
### Environment Variables
This project uses a `.env` file to manage environment variables. You need to create this file in the root directory of your project. The `.env` file should contain the following variables:
