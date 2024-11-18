import { randomUUID } from 'crypto';
import { JSDOM } from 'jsdom';
import puppeteer from 'puppeteer';

function number2letter(number) {
  const alphabet = 'abcdefghijklmnopqrstuvwxyz';
  return alphabet[number - 1];
}

async function handleSubSubPoint(_subSubPoint) {
  const subSubPoint = new JSDOM('<!DOCTYPE html>' + _subSubPoint).window.document.body.children[0];
  const directText = Array.from(subSubPoint.childNodes)
    .filter((n) => n.nodeType === 3) // Node type 3 is a text node
    .map((n) => n.textContent.trim())
    .filter(Boolean)
    .join(' ');

  return directText;
}

async function handleSubPoint(_subPoint, number) {
  // subPoint is a li element
  const result = {};
  const subPoint = new JSDOM('<!DOCTYPE html>' + _subPoint).window.document.body.children[0];
  const directText = Array.from(subPoint.childNodes)
    .filter((n) => n.nodeType === 3) // Node type 3 is a text node
    .map((n) => n.textContent.trim())
    .filter(Boolean)
    .join(' ');

  if (subPoint.children.length > 0) {
    result[await randomUUID()] = {
      classType: 'SUBPOINT',
      number,
      content: directText,
    };
    let subSubPointNumber = 0;
    for (const subSubPoint of Array.from(subPoint.children)) {
      if (subSubPoint.tagName === 'P') {
        result[await randomUUID()] = {
          classType: 'SUBSUBPOINT',
          number: (await number2letter(++subSubPointNumber)) + ')',
          content: subSubPoint.textContent.trim(),
        };
      } else {
        for (const child of Array.from(subSubPoint.children)) {
          result[await randomUUID()] = {
            classType: 'SUBSUBPOINT',
            number: (await number2letter(++subSubPointNumber)) + ')',
            content: await handleSubSubPoint(child.outerHTML),
          };
        }
      }
    }
  } else {
    return directText;
  }

  return result;
}

async function handlePoint(_point, number) {
  // point is a li element
  const result = {};
  const point = new JSDOM('<!DOCTYPE html>' + _point).window.document.body.children[0];

  const directText = Array.from(point.childNodes)
    .filter((n) => n.nodeType === 3) // Node type 3 is a text node
    .map((n) => n.textContent.trim())
    .filter(Boolean)
    .join(' ');

  if (point.children.length > 0) {
    result[await randomUUID()] = {
      classType: 'POINT',
      number,
      content: directText,
    };
    let subPointNumber = 0;
    for (const subPoint of Array.from(point.children)) {
      if (subPoint.tagName === 'P') {
        result[await randomUUID()] = {
          classType: 'SUBPOINT',
          number: await randomUUID(),
          content: subPoint.textContent.trim(),
        };
      } else {
        for (const child of Array.from(subPoint.children)) {
          result[await randomUUID()] = {
            classType: 'SUBPOINT',
            number: ++subPointNumber,
            content: await handleSubPoint(child.outerHTML, subPointNumber),
          };
        }
      }
    }
  } else {
    return directText;
  }

  return result;
}

async function handleArticlePage() {
  const title = document.querySelector('.dsgvo-title').innerHTML.trim();
  const articleNumber = document.querySelector('.dsgvo-number').innerHTML.trim();
  const relatedArticles = Array.from(document.querySelectorAll('.empfehlung-dsgvo-artikel a')).map(
    (article) => article.href.match(/art-(\d+)-dsgvo/)[1]
  );

  const points = {};
  let number = 0;
  for (const point of Array.from(document.querySelectorAll('.entry-content>ol')).concat(
    Array.from(document.querySelectorAll('.entry-content>p'))
  )) {
    if (point.tagName === 'P') {
      points[await randomUUID()] = {
        classType: 'POINT',
        number: ++number,
        content: point.textContent.trim(),
      };
    } else {
      for (const child of Array.from(point.children)) {
        points[await randomUUID()] = {
          classType: 'POINT',
          number: ++number,
          content: await handlePoint(child.outerHTML, number),
        };
      }
    }
  }

  return {
    classType: 'ARTICLE',
    relatedArticles,
    content: {
      [await randomUUID()]: {
        classType: 'TITLE_ID',
        content: 'Artikel ' + articleNumber.match(/\d+/)[0],
      },
      [await randomUUID()]: {
        classType: 'TITLE',
        content: title,
      },
      ...points,
    },
  };
}

const main = async () => {
  // Start a Puppeteer session with:
  // - a visible browser (`headless: false` - easier to debug because you'll see the browser in action)
  // - no default viewport (`defaultViewport: null` - website page will be in full width and height)
  const browser = await puppeteer.launch({
    headless: false,
    defaultViewport: null,
  });

  // Open a new page
  const page = await browser.newPage();
  const articles = {};

  // On this new page:
  // - wait until the dom content is loaded (HTML is ready)
  await page.goto('https://dsgvo-gesetz.de/bdsg', {
    waitUntil: 'domcontentloaded',
  });

  // Get all the articles'links on the page
  const articleLinks = await page.evaluate(() => {
    // Fetch all the elements with class "entry-title"
    // Get the href attribute and return it
    const articleList = document.querySelectorAll('.artikel a');
    return Array.from(articleList).map((article) => article.href);
  });

  const articlePage = await browser.newPage();
  // Expose the Node.js function to the browser context
  await articlePage.exposeFunction('randomUUID', randomUUID);
  await articlePage.exposeFunction('handlePoint', handlePoint);
  await articlePage.exposeFunction('handleSubPoint', handleSubPoint);
  await articlePage.exposeFunction('handleSubSubPoint', handleSubSubPoint);
  await articlePage.exposeFunction('number2letter', number2letter);

  for (const articleLink of articleLinks) {
    // Open a new page
    await articlePage.goto(articleLink, {
      waitUntil: 'domcontentloaded',
    });

    // Get the article content
    const article = await articlePage.evaluate(handleArticlePage);

    articles[articleLink] = article;
  }

  await browser.close();
  return articles;
};

export default main;
