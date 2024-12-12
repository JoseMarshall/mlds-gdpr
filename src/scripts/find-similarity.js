const keywordExtractor = require('keyword-extractor');

// Utility to extract keywords from text
const extractKeywords = (text) => {
  return keywordExtractor.extract(text, {
    language: 'english',
    remove_digits: false,
    return_changed_case: true,
    remove_duplicates: true,
  });
};

// Utility to check if article numbers are mentioned
const extractArticleNumbers = (text) => {
  const match = text.match(/\b(?:article|art)\s*\d+\b/gi);
  return match ? match.map((num) => num.toLowerCase()) : [];
};

// Function to determine if two articles are related
const areArticlesRelated = ({ article1, article2, keywordThreshold = 0.5 }) => {
  const keywords1 = new Set(extractKeywords(article1));
  const keywords2 = new Set(extractKeywords(article2));

  // Calculate keyword overlap
  const commonKeywords = [...keywords1].filter((keyword) => keywords2.has(keyword));
  const keywordSimilarity = commonKeywords.length / Math.max(keywords1.size, keywords2.size);

  // Check if article numbers are mentioned
  const articleNumbers1 = extractArticleNumbers(article1);
  const articleNumbers2 = extractArticleNumbers(article2);

  const mentionsArticleNumber =
    articleNumbers1.some((num) => article2.toLowerCase().includes(num)) ||
    articleNumbers2.some((num) => article1.toLowerCase().includes(num));

  return keywordSimilarity >= keywordThreshold || mentionsArticleNumber;
};

module.exports = { areArticlesRelated };
