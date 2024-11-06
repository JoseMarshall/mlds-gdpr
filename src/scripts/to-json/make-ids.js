const { randomUUID } = require('crypto');
const fs = require('fs');
const path = require('path');

// create a write stream on the file id.json
const writeStream = fs.createWriteStream(path.resolve(__dirname, 'ids.json'));

// generate 100000 random ids and write them to the file
writeStream.write('[');
for (let i = 0; i < 1000000; i++) {
  writeStream.write(`"${randomUUID()}",\n`);
}
writeStream.write(']');
writeStream.end();
writeStream.on('finish', () => {
  console.log('File written successfully ✅');
});
