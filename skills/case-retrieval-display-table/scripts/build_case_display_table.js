#!/usr/bin/env node

const fs = require("fs");
const path = require("path");
const {
  AlignmentType,
  BorderStyle,
  Document,
  ExternalHyperlink,
  Footer,
  Packer,
  PageBreak,
  PageOrientation,
  Paragraph,
  ShadingType,
  Table,
  TableCell,
  TableLayoutType,
  TableRow,
  TextRun,
  UnderlineType,
  VerticalAlign,
  WidthType,
} = require("docx");

const args = process.argv.slice(2);
const valueAfter = (flag) => {
  const index = args.indexOf(flag);
  return index >= 0 ? args[index + 1] : undefined;
};
const inputPath = valueAfter("--input");
const outputPath = valueAfter("--output");
const reportTitle = valueAfter("--title") || "[律所名称]｜类案检索案例展示表";
const footerLabel = valueAfter("--footer") || "[律所名称]｜类案检索案例展示表";
const creatorName = valueAfter("--creator") || "[律所名称]";

if (!outputPath) {
  console.error("Usage: node build_case_display_table.js --output output.docx [--input cases.json] [--title title] [--footer footer] [--creator name]");
  process.exit(2);
}

const clean = (value, fallback = "公开材料未载明") => {
  if (value === undefined || value === null || String(value).trim() === "") return fallback;
  return String(value).trim();
};

const firstClean = (values, fallback = "公开材料未载明") => {
  for (const value of values) {
    if (value !== undefined && value !== null && String(value).trim() !== "") return String(value).trim();
  }
  return fallback;
};

const blankCase = () => ({
  classification: "〔检索分类〕",
  title: "〔填写案件全称；将本行文字设置为判决原文超链接〕",
  court: "〔法院名称；如有一、二审，按“一审；二审”填写〕",
  caseNumber: "〔案号〕",
  decisionDate: "〔裁判日期〕",
  procedure: "〔一审／二审；判决书／裁定书〕",
  caseNature: "〔例如：二审民事判决书；二审民事管辖裁定〕",
  keyExpressions: "〔摘录与检索主题、裁判判断或争点识别有关的关键词、合同条款、争议表述或裁判用语；没有则写“未见与本案认定相关的关键词”〕",
  issues: "〔只写与案件判断直接相关的主体、行为、请求、抗辩、事实和争点；建议 150-300 字〕",
  findings: "〔依据“本院认为”压缩归纳判断路径与证据边界；不要把当事人主张改写为法院结论；建议 200-400 字〕",
  disposition: "〔摘录裁判主文；二审应写明“驳回上诉／维持原判／改判”等〕",
});

let payload = { cases: [blankCase()] };
if (inputPath) {
  payload = JSON.parse(fs.readFileSync(inputPath, "utf8"));
  if (Array.isArray(payload)) payload = { cases: payload };
  if (!Array.isArray(payload.cases) || payload.cases.length === 0) {
    throw new Error("Input must contain a non-empty cases array.");
  }
}

const FONT = "宋体";
const HEADER_BLUE = "D9EAF7";
const LABEL_BLUE = "DDEBF7";
const BLACK = "000000";
const LINK_BLUE = "0563C1";
const PAGE_SHORT = 11906;
const PAGE_LONG = 16838;
const MARGIN = 780;
const TABLE_WIDTH = PAGE_LONG - MARGIN * 2;
const LABEL_WIDTH = 1650;
const CONTENT_WIDTH = TABLE_WIDTH - LABEL_WIDTH;
const border = { style: BorderStyle.SINGLE, size: 5, color: BLACK };
const borders = { top: border, bottom: border, left: border, right: border, insideHorizontal: border, insideVertical: border };

function run(text, options = {}) {
  return new TextRun({ text: clean(text, ""), font: FONT, size: options.size || 20, bold: options.bold || false, color: options.color, underline: options.underline });
}

function paragraph(content, options = {}) {
  const children = Array.isArray(content) ? content : [run(content, options)];
  return new Paragraph({
    children,
    alignment: options.alignment || AlignmentType.LEFT,
    spacing: { before: options.before || 0, after: options.after || 0, line: options.line || 280 },
  });
}

function ordinaryCell(content, width, options = {}) {
  const body = Array.isArray(content) ? content : [paragraph(content, options)];
  return new TableCell({
    width: { size: width, type: WidthType.DXA },
    borders,
    shading: options.shading ? { fill: options.shading, type: ShadingType.CLEAR } : undefined,
    margins: { top: options.top ?? 80, bottom: options.bottom ?? 80, left: 120, right: 120 },
    verticalAlign: options.verticalAlign || VerticalAlign.CENTER,
    children: body,
  });
}

function titleCell(item) {
  const text = clean(item.title, "〔填写案件全称〕");
  const hyperlink = item.url
    ? new ExternalHyperlink({ link: item.url, children: [run(text, { color: LINK_BLUE, underline: { type: UnderlineType.SINGLE } })] })
    : run(text, { color: item.title && !String(item.title).startsWith("〔") ? BLACK : LINK_BLUE, underline: item.title && !String(item.title).startsWith("〔") ? undefined : { type: UnderlineType.SINGLE } });
  return ordinaryCell([paragraph([hyperlink])], CONTENT_WIDTH, { top: 95, bottom: 95 });
}

function row(label, content, options = {}) {
  return new TableRow({
    cantSplit: true,
    children: [
      ordinaryCell([paragraph(label, { bold: true, alignment: AlignmentType.CENTER, line: 280 })], LABEL_WIDTH, { shading: LABEL_BLUE, top: 95, bottom: 95 }),
      ordinaryCell(content, CONTENT_WIDTH, { top: options.top ?? 95, bottom: options.bottom ?? 95, verticalAlign: options.verticalAlign || VerticalAlign.TOP }),
    ],
  });
}

function textValue(item, key, placeholder) {
  return clean(item[key], placeholder);
}

function caseTable(item, index) {
  const category = clean(item.classification, "〔检索分类〕");
  const metadata = [
    textValue(item, "caseNumber", "〔案号〕"),
    textValue(item, "decisionDate", "〔裁判日期〕"),
    textValue(item, "procedure", "〔一审／二审；判决书／裁定书〕"),
  ].join("；");
  const keyExpressions = firstClean([item.keyExpressions, item.derogatoryTerms], "〔关键表述／关键词〕");
  return new Table({
    width: { size: 100, type: WidthType.PERCENTAGE },
    columnWidths: [LABEL_WIDTH, CONTENT_WIDTH],
    layout: TableLayoutType.FIXED,
    borders,
    rows: [
      new TableRow({
        cantSplit: true,
        children: [
          new TableCell({
            columnSpan: 2,
            width: { size: TABLE_WIDTH, type: WidthType.DXA },
            borders,
            shading: { fill: HEADER_BLUE, type: ShadingType.CLEAR },
            margins: { top: 95, bottom: 95, left: 120, right: 120 },
            children: [paragraph(`案例 ${index}｜${category}`, { bold: true, size: 22, alignment: AlignmentType.CENTER })],
          }),
        ],
      }),
      new TableRow({ cantSplit: true, children: [ordinaryCell([paragraph("案件名称", { bold: true, alignment: AlignmentType.CENTER })], LABEL_WIDTH, { shading: LABEL_BLUE }), titleCell(item)] }),
      row("审理法院", textValue(item, "court", "〔法院名称〕")),
      row("案号／日期／程序", metadata),
      row("案件性质", textValue(item, "caseNature", "〔案件性质〕")),
      row("关键表述／关键词", keyExpressions),
      row("核心事实／争点", textValue(item, "issues", "〔核心事实／争点〕"), { top: 105, bottom: 105 }),
      row("法院认定", textValue(item, "findings", "〔法院认定〕"), { top: 105, bottom: 105 }),
      row("裁判结果", textValue(item, "disposition", "〔裁判结果〕")),
    ],
  });
}

const date = new Date().toISOString().slice(0, 10).replaceAll("-", ".");
const body = [
  new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { before: 0, after: 120 },
    children: [run(reportTitle, { bold: true, size: 28 })],
  }),
  new Paragraph({
    alignment: AlignmentType.LEFT,
    spacing: { before: 0, after: 130, line: 260 },
    children: [run("填写提示：案件名称本身链接至裁判原文。按“实体判决／程序或关联裁定／重复题录／典型案例”标明检索分类；无法由公开材料核验的事项，填写“公开材料未载明”。", { size: 18 })],
  }),
];

payload.cases.forEach((item, index) => {
  if (index > 0) body.push(new Paragraph({ children: [new PageBreak()] }));
  body.push(caseTable(item, index + 1));
});

const document = new Document({
  creator: creatorName,
  title: reportTitle,
  styles: {
    default: { document: { run: { font: FONT, size: 20 } } },
  },
  sections: [{
    properties: {
      page: {
        size: { width: PAGE_SHORT, height: PAGE_LONG, orientation: PageOrientation.LANDSCAPE },
        margin: { top: 620, right: MARGIN, bottom: 620, left: MARGIN },
      },
    },
    footers: {
      default: new Footer({ children: [paragraph(`${footerLabel}｜${date}`, { size: 16, alignment: AlignmentType.CENTER })] }),
    },
    children: body,
  }],
});

fs.mkdirSync(path.dirname(path.resolve(outputPath)), { recursive: true });
Packer.toBuffer(document).then((buffer) => {
  fs.writeFileSync(outputPath, buffer);
  console.log(`Created: ${path.resolve(outputPath)}`);
});
