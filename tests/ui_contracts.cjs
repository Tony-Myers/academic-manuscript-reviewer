// Independently authored generic UI and passage contracts. No inherited fixtures.
const assert=require('node:assert/strict'), fs=require('node:fs'), path=require('node:path'),vm=require('node:vm');
const root=path.join(__dirname,'..');const html=fs.readFileSync(path.join(root,'app/chat.html'),'utf8');
const context=vm.createContext({BASE:'',FINDING_ID:/^(S|C|P)\d+$/,console});
function load(name){
 const start=html.search(new RegExp('^(?:async )?function '+name+'\\(','m'));
 assert(start>=0,'missing '+name);const tail=html.slice(start);
 const next=tail.slice(1).search(/\n(?:async )?function /);
 vm.runInContext(next<0?tail:tail.slice(0,next+1),context);
}
for(const name of ['esc','renderMd','splitCriticalAppraisal','documentViewerUrl','evidenceCardsWorkspaceUrl','savedReviewsNotice'])load(name);
const rendered=context.renderMd('# Bench\n\n**Tile** and *signal*.\n\n| Colour | Units |\n| --- | --- |\n| Teal | 8.2 |\n\n<script>unsafe</script>');
assert(rendered.includes('<strong>Tile</strong>'));assert(rendered.includes('<em>signal</em>'));
assert(rendered.includes('<table>'));assert(rendered.includes('8.2'));assert(!rendered.includes('<script>'));
// Backslash escapes, ordinary formatting and unsafe text in the shared renderer.
const esc1=context.renderMd('\\*\\*Reason:\\*\\* fixture');
assert(esc1.includes('**Reason:** fixture'));assert(!esc1.includes('\\'));assert(!esc1.includes('<strong>'));
assert(context.renderMd('**Reason:** fixture').includes('<strong>Reason:</strong>'));
assert(context.renderMd('a \\\\ b').includes('a \\ b'));
const unsafe=context.renderMd('<script>alert(1)</script> \\<img src=x onerror=alert(1)\\> [x](javascript:alert(1))');
assert(!/<script|<img|href="javascript/i.test(unsafe));assert(unsafe.includes('&lt;script&gt;'));
assert(context.renderMd('C:\\Users\\fixture').includes('C:\\Users\\fixture'));
const raw='Model: fixture\n\n# Overall synopsis\nIndependent fixture.\n\n# Source verification record\nMock record.\n';
const split=context.splitCriticalAppraisal(raw);assert.equal(split.technical+split.appraisal+split.audit,raw);
assert(split.technical.includes('Model:'));assert(!split.appraisal.includes('Mock record.'));assert(split.audit.includes('Mock record.'));
assert.equal(context.documentViewerUrl('ab12cd34ef56','d1',2),'/review/document-viewer#job=ab12cd34ef56&doc=d1&page=2');
assert(!context.documentViewerUrl('ab12cd34ef56',null,2).includes('page='));
assert(context.evidenceCardsWorkspaceUrl('ab12cd34ef56','C2').includes('&view=cards&card=C2'));
// Server status wording: who manages the server, connection and model state
// are reported separately and never collapsed into one "not reachable".
load('describeServerStatus');
const st=(o)=>context.describeServerStatus(Object.assign({mode:'managed',server_url:'http://127.0.0.1:8081',connection:'connected',model_state:'loaded',loaded_model:'beta-synthetic.gguf',switch:{state:'idle'}},o));
assert.equal(context.describeServerStatus(null,false).text,'App not reachable');
assert.equal(context.describeServerStatus(null,true).text,'Restarting the app...');
assert.equal(st({}).text,'beta-synthetic.gguf (managed server)');assert.equal(st({}).dot,'connected');
assert.equal(st({mode:'external',connection:'unreachable',model_state:'unknown',loaded_model:null}).text,'Server unreachable (external server)');
const loading=st({model_state:'loading',connection:'unreachable',switch:{state:'loading',target_name:'gamma-synthetic.gguf'}});
assert.equal(loading.text,'Loading gamma-synthetic.gguf (managed server)');assert.equal(loading.dot,'loading');
const failed=st({model_state:'failed',message:'Model failed to load: ERROR: fixture'});
assert.equal(failed.dot,'error');assert(failed.title.includes('ERROR: fixture'));
assert.equal(st({mode:'external',loaded_model:null}).text,'model not reported (external server)');
assert(st({model_matches_configured:false}).text.includes('differs from selection'));
// Vision wording: a result is shown only for the model it was recorded with.
load('visionStatusText');
const vis=(status,extra)=>context.visionStatusText(Object.assign({image_input:'confirmed',source:'fixture',page_rendering:'available',
  vision_test:{status,model:'alpha-synthetic.gguf',scope:'image requests to alpha-synthetic.gguf',last_at:'t',last_success_at:'t'}},extra||{}));
assert.equal(vis('succeeded').word,'vision: available, tested');
assert.equal(vis('failed').word,'vision: reported available, last test failed');
assert.equal(vis('not_tested').word,'vision: reported available, not yet tested');
assert.equal(vis('unknown_model').word,'vision: reported available, not yet tested');
assert.equal(vis('succeeded',{page_rendering:'unavailable (pypdfium2 not installed)'}).word,'vision: reported available; page rendering not installed');
assert.equal(vis('succeeded',{image_input:'unavailable'}).word,'vision: unavailable');
// Print buttons for the Critical Appraisal and appendix tabs: new tab, dedicated page.
load('printPageUrl');load('printBarHtml');
assert.equal(context.printPageUrl('ab12cd34ef56','appraisal'),'/review/ab12cd34ef56/print/appraisal');
assert.equal(context.printPageUrl('ab12cd34ef56','appendix'),'/review/ab12cd34ef56/print/appendix');
const bar=context.printBarHtml('appendixPrintBar','ab12cd34ef56','appendix','Print / Save Human Evidence Appendix as PDF',false);
assert(bar.includes('target="_blank"'));assert(bar.includes('style="display:none"'));assert(bar.includes('Print / Save Human Evidence Appendix as PDF'));
assert.equal(context.printBarHtml('x','','appraisal','Label',true),'');
// A review store that cannot be used, or a save that failed, is stated, never shown as an empty list.
assert.equal(context.savedReviewsNotice({path:'/x',error:''},null),'');
assert(context.savedReviewsNotice({path:'/x',error:'The configured review store /x does not exist.'},null).includes('does not exist'));
assert(context.savedReviewsNotice(null,{job_id:'ab12cd34ef56',error:'disk full'}).includes('could not be saved: disk full'));
const matcher=require('../passage_match/passage_match.js');
const item=str=>({str,transform:[11,0,0,11,50,700],width:str.length*6,height:11});
const page=(n,...text)=>({page:n,items:text.map(item)});
const quote='The sensor measured a teal ceramic tile.';
assert.equal(matcher.locatePassage([page(1,quote)],quote).status,'exact');
assert.equal(matcher.locatePassage([page(1,quote),page(2,quote)],quote).status,'ambiguous');
assert.equal(matcher.locatePassage([page(1,quote),page(2,quote)],quote,2).page,2);
assert.equal(matcher.locatePassage([page(1,'No matching sentence.')],quote).status,'not_found');
assert.equal(matcher.locatePassage([{page:1,items:[]}],quote).status,'no_text_layer');
assert.equal(matcher.canonQuote('A ﬁne tile − 2'),'A fine tile - 2');
console.log('52 independent UI/passage assertions passed');
