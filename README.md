# GymBrain 🏋️🧠

GymBrain is an AI-powered gym exercise recommender that uses Google's Gemini and Langchain's infrastructure to deliver a personalised workout plan directly to your WhatsApp every morning.

![image](https://github.com/user-attachments/assets/367657e1-eaa9-4805-915e-f89f39b5021e) ![image](https://github.com/user-attachments/assets/d38b6eef-ce00-4760-85ad-10d21efa814d) ![image](https://github.com/user-attachments/assets/60a82d8c-d787-4874-9b8d-054d319862cd)


---

## How it Works:

#### Step 1: Scraping Exercises from PureGym's YouTube Playlist
We scrape a list of gym exercises from PureGym’s official YouTube playlist. This data is then carefully structured for further processing.

https://youtube.com/playlist?list=PLsliPlpqH8JD9Iy1A3WiiSEGPMvpX3voq&feature=shared

#### Step 2: Upload Your Latest Health Report
Upload your most recent health report, which is analysed to assess your vitals and create a customised gym plan that suits your fitness goals.

#### Step 3: Data Processing & Prompt Engineering
We apply advanced prompt engineering to process the scraped data and format the exercises in a user-friendly list. Each exercise comes with a YouTube video link to guide you through proper execution.

Updating the Prompts with Fitness Goals

#### Step 4: WhatsApp Integration with Twilio
All of this is integrated with Twilio’s WhatsApp API, ensuring you receive a daily WhatsApp message with a list of exercises, complete with links to video demonstrations.

---

## Demo WhatsApp Message:
You will receive a message on WhatsApp each morning containing the names of the exercises and links to the instructional YouTube videos.

Demo Whatsapp Message:

<img width="294" alt="Screenshot 2024-11-30 at 20 02 23" src="https://github.com/user-attachments/assets/85a9f17c-2b4e-47ba-94a9-ad62633954d5">

