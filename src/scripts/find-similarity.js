const keywordExtractor = require('keyword-extractor');

// Utility to extract keywords from text
const extractKeywords = (text) => {
  return keywordExtractor.extract(text, {
    language: 'portuguese',
    remove_digits: false,
    return_changed_case: true,
    remove_duplicates: true,
  });
};

// Utility to check if article numbers are mentioned
const extractArticleNumbers = (text) => {
  const match = text.match(/\b(?:artigo|art)\s*(\d+)\b/gi);
  return match ? match.map((num) => num.match(/(\d+)/)[1]) : [];
};

function calcSimilarity(txt1, txt2) {
  const keywords1 = new Set(extractKeywords(txt1));
  const keywords2 = new Set(extractKeywords(txt2));
  const commonKeywords = [...keywords1].filter((keyword) => keywords2.has(keyword));
  return commonKeywords.length / Math.max(keywords1.size, keywords2.size);
}

// Function to determine if two articles are related
const areArticlesRelated = ({ article1, article2, keywordThreshold = 0.9 }) => {
  const content1 = article1.points.join(' ');
  const content2 = article2.points.join(' ');

  // Check if article numbers are mentioned
  const articleNumbers1 = extractArticleNumbers(content1);
  const articleNumbers2 = extractArticleNumbers(content2);

  const mentionsArticleNumber =
    articleNumbers1.some((num) => article2.path.match(/(\d+)$/)[1] == num) ||
    articleNumbers2.some((num) => article1.path.match(/(\d+)$/)[1] == num);

  return (
    calcSimilarity(article1.title, article2.title) >= 0.5 ||
    mentionsArticleNumber ||
    calcSimilarity(content1, content2) >= keywordThreshold
  );
};

module.exports = { areArticlesRelated };
