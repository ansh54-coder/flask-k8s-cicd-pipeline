# ShopAPI Architecture

## Overview

ShopAPI is a Flask REST API for products, users and orders.

The application follows a layered architecture:

```text
Client
  |
  v
Ingress
  |
  v
Kubernetes Service
  |
  v
Flask API
  |
  +----------------+
  |                |
  v                v
PostgreSQL       Redis
