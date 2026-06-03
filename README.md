# Real-Time News Intelligence Platform

## Project Overview

The Real-Time News Intelligence Platform is a system designed to collect, process, analyze, and visualize news data from multiple trusted news sources in near real-time. The platform aims to provide intelligent news search, temporal analytics, event tracking, and AI-powered insights using technologies such as Kafka, Elasticsearch, MongoDB, and Agentic AI.

---

## Day 1 Progress

### Objective

To understand and implement the first stage of the data pipeline: News Crawling.

### Tasks Completed

* Created GitHub repository structure.
* Installed and configured Python environment.
* Installed the `feedparser` library.
* Connected to a live BBC RSS feed.
* Retrieved real-time news articles.
* Extracted article metadata:

  * Title
  * Link
  * Publication Date
* Displayed news articles in the console.

---

## Technologies Used

* Python
* Feedparser
* Git
* GitHub

---

## Current Architecture

RSS Feed (BBC)
↓
Python Crawler
↓
Article Metadata Extraction
↓
Console Output

---

## Learning Outcomes

### RSS Feed

RSS provides structured and continuously updated news content from publishers.

### Feedparser

Feedparser converts RSS/XML feeds into Python objects that are easy to process.

### Metadata Extraction

The crawler successfully extracts:

* Article Title
* Article URL
* Publication Timestamp

These fields will be required later for:

* Elasticsearch Indexing
* Search Functionality
* Temporal Analytics
* Event Timeline Generation

---

## Future Work

### Day 2

* Add multiple news sources.
* Create a centralized RSS source configuration.
* Convert article data into structured JSON format.
* Store collected articles in a JSON file.

### Upcoming Modules

* Kafka Integration
* Elasticsearch Indexing
* MongoDB Storage
* Real-Time Dashboard
* Agentic AI Search Layer
* Temporal Analytics
* Event Timeline Generation

---

## Project Status

Phase 1: Crawling Module

Status: Completed ✅

