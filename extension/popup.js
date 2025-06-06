const words = [
  { word: "apple", meaning: "a fruit" },
  { word: "ball", meaning: "a round toy" },
  { word: "cat", meaning: "a small animal" },
  { word: "dog", meaning: "a friendly animal" },
  { word: "egg", meaning: "something you eat for breakfast" },
  { word: "fish", meaning: "an animal that swims" },
  { word: "go", meaning: "to move" },
  { word: "hat", meaning: "something you wear on your head" },
  { word: "ice", meaning: "frozen water" },
  { word: "juice", meaning: "a fruity drink" }
];

function showRandomWord() {
  const random = words[Math.floor(Math.random() * words.length)];
  const el = document.getElementById('word');
  el.textContent = `${random.word} - ${random.meaning}`;
}

document.getElementById('next').addEventListener('click', showRandomWord);
showRandomWord();
