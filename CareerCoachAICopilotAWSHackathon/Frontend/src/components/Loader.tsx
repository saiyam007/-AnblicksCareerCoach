import React, { useEffect, useState } from "react";
import { ImageWithFallback } from "./figma/ImageWithFallback";

const messages = [
  // 🌍 General Facts & Curiosity (Expanded & Storytelling Style)
  "Did you know? The Eiffel Tower actually grows taller in summer. When the iron heats up, it expands, making the tower nearly 15 cm taller. So yes, even buildings have summer glow-ups ☀️🏗️.",
  "Here’s a mind-bender: bananas are technically berries, but strawberries aren’t. Nature clearly doesn’t care about your fruit logic 🍌🍓.",
  "Honey never spoils. Archaeologists once discovered pots of honey in ancient Egyptian tombs that were over 3,000 years old — and still perfectly edible. Sweet history, literally 🍯⏳.",
  "The heart of a blue whale is so massive that a human could literally crawl through its arteries. It beats slowly… only a few times per minute. That’s one chill giant 🐋❤️.",
  "An octopus has three hearts, blue blood, and can change its skin color in seconds. Basically, it’s a real-life alien living in our oceans 🐙🌊.",
  "Contrary to popular myth, the Great Wall of China isn’t visible from space. Astronauts have confirmed it — space doesn’t work like a zoom lens 🛰️🏯.",
  "A day on Venus is actually longer than a year on Venus. Imagine celebrating your birthday before the day even ends. Cosmic time is weird 🪐⏳.",
  "Butterflies can taste with their feet — imagine stepping on cake and immediately knowing how sweet it is 🦋🍰.",
  "Try it now: hum with your nose closed. Yep, can’t be done. Science just loves proving us wrong in the simplest ways 🤭🎶.",
  "Sharks existed before trees. Let that sink in. There were sharks swimming in ancient oceans hundreds of millions of years ago while land was still figuring itself out 🦈🌿.",
  "Raindrops don’t fall as perfect teardrops — they’re shaped more like tiny hamburger buns. So the next time it rains, imagine the sky flipping burgers 🍔☔.",
  "The first oranges weren’t orange. They were green — and they still are in many warm climates today. Color was just a late branding decision 🍊🌱.",
  "Cleopatra lived closer in time to the Moon landing than to the building of the pyramids. History isn’t as linear as it looks 🏺🚀.",
  "Cows actually have best friends and get stressed when they’re separated. Yes, even cows need emotional support 🐄💞.",
  "There are more stars in the universe than grains of sand on Earth’s beaches. Let that sink in as your brain does a backflip 🌌✨.",
 
  // 💡 Inspirational / Motivational (Longer & More Reflective)
  "Great things take time — just like this moment. Behind the scenes, bits and bytes are dancing in perfect rhythm to bring something meaningful to you. ⏳✨",
  "Every second you wait isn’t wasted — it’s fueling the creation of something crafted with care, precision, and a touch of brilliance. ⚡",
  "Curiosity is the spark behind everything extraordinary. Even this short pause is part of a bigger story unfolding just for you. 🌱",
  "Patience isn’t just waiting — it’s trusting that something remarkable is on its way. And right now, it is. 🌟",
  "Progress doesn’t always make noise. Sometimes, the most powerful transformations happen in silence before they shine. 🌿",
  "Innovation often begins with a quiet moment like this — a pause before the breakthrough. 🧠💡",
  "Big things usually start small. What seems like a loading bar might actually be the beginning of something exciting. 🚀",
  "Something amazing is forming in the digital background — algorithms aligning, data syncing, ideas crystallizing. 🌐✨",
  "Stay curious. Every second here is a seed being planted for something smarter, faster, and more brilliant. 🌸",
  "Calm minds notice more. Good things — like the one loading right now — often arrive just after a breath of stillness. 🌬️🌟",
  "Dreams take time to form. So does great data. Trust the process. ⏳",
  "You’re not just waiting. You’re standing at the doorstep of something cool. 🪄",
  "This short pause is where things quietly shift from ‘idea’ to ‘reality.’ 🧭✨",
  "Sometimes, the best results don’t rush. They arrive fashionably late… but worth the wait. 👑",
  "Great outcomes don’t happen instantly — they’re built moment by moment. Like right now. 🛠️",
 
  // 🌟 Engaging Thoughts / Quotes (With Context & Storytelling)
  "“The future belongs to those who prepare for it today.” – Malcolm X. Every second here isn’t lost time — it’s preparation for what comes next. 🕰️🌟",
  "“Stay hungry, stay foolish.” – Steve Jobs. Even a loading moment can be a reminder to keep your spark alive. 🔥",
  "“In the middle of difficulty lies opportunity.” – Albert Einstein. What feels like waiting might just be the calm before something brilliant. 🧠✨",
  "“It always seems impossible until it’s done.” – Nelson Mandela. And then it feels inevitable. Just a few more seconds. 💪",
  "“Don’t watch the clock; do what it does — keep going.” – Sam Levenson. Time isn’t lost — it’s simply moving forward with you. ⏳",
  "“Simplicity is the ultimate sophistication.” – Leonardo da Vinci. The best outcomes are often quietly crafted. 🎨✨",
  "“A journey of a thousand miles begins with a single step.” – Lao Tzu. And maybe this moment is that step. 🛤️",
  "“Knowledge speaks, but wisdom listens.” – Jimi Hendrix. Silence — even during loading — can be surprisingly wise. 🎧",
  "“The secret of getting ahead is getting started.” – Mark Twain. Which is exactly what’s happening behind the scenes right now. ⚡",
  "“Curiosity is the spark behind every great idea.” — and it’s also why you’re still reading this instead of checking your notifications 😉🔥",
];



function getShuffledMessages() {
  return [...messages].sort(() => Math.random() - 0.5);
}

function Loader() {
  const [messageList, setMessageList] = useState<string[]>(getShuffledMessages());
  const [messageIndex, setMessageIndex] = useState(0);
  const [displayedText, setDisplayedText] = useState("");
  const [charIndex, setCharIndex] = useState(0);

  // Typing effect
  useEffect(() => {
    const currentMessage = messageList[messageIndex];
    if (charIndex < currentMessage.length) {
      const timeout = setTimeout(() => {
        setDisplayedText((prev) => prev + currentMessage.charAt(charIndex));
        setCharIndex((prev) => prev + 1);
      }, 40);
      return () => clearTimeout(timeout);
    } else {
      // Wait before next message
      const timeout = setTimeout(() => {
        if (messageIndex < messageList.length - 1) {
          setMessageIndex((prev) => prev + 1);
        } else {
          // Restart with new random set
          setMessageList(getShuffledMessages());
          setMessageIndex(0);
        }
        setDisplayedText("");
        setCharIndex(0);
      }, 4000);
      return () => clearTimeout(timeout);
    }
  }, [charIndex, messageIndex, messageList]);

  return (
    <div style={overlayStyle}>
      <div style={textStyle}>
        <div className="d-flex flex-column align-items-center">
          <div className="align-items-center bg-white d-flex justify-content-center rounded-3 rounded-circle loading-circle">
            <ImageWithFallback
              src="assets/logo.svg"
              alt="Anblicks AI Career Coaching"
              className="p-3"
            />
          </div>

          {/* Dynamic message */}
          <div className="fs-5 mt-3 fw-medium text-white" style={{ minWidth: "90%" }}>
            {displayedText}
            <span className="text-warning animate-blink">|</span>
          </div>
        </div>
      </div>
    </div>
  );
}

const overlayStyle: React.CSSProperties = {
  position: "fixed",
  top: 0,
  left: 0,
  width: "100vw",
  height: "100vh",
  backgroundColor: "rgba(0, 0, 0, 0.6)",
  display: "flex",
  alignItems: "center",
  justifyContent: "center",
  zIndex: 9999,
  padding: "1rem",
  textAlign: "center",
};

const textStyle: React.CSSProperties = {
  color: "#fff",
  fontWeight: 500,
  textAlign: "center",
};

export default React.memo(Loader);
