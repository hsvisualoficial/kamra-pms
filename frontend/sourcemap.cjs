const fs = require('fs');
const sourceMap = require('source-map');
const mapData = fs.readFileSync('../kamra/public/frontend/assets/index-CfW8Mm74.js.map', 'utf8');

async function locate() {
  const smc = await new sourceMap.SourceMapConsumer(mapData);
  const pos = smc.originalPositionFor({
    line: 501,
    column: 61781
  });
  console.log(pos);
  smc.destroy();
}
locate();
