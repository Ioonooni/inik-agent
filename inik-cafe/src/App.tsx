import { useState, useEffect, useRef, useCallback, type Dispatch, type SetStateAction } from "react";

type PageId = 'home' | 'chat' | 'memories' | 'journey' | 'profile' | 'about';
type SetPage = Dispatch<SetStateAction<PageId>>;

const CSS = `
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;0,900;1,400&family=Inter:wght@300;400;500;600&display=swap');
*{box-sizing:border-box;margin:0;padding:0}
::-webkit-scrollbar{width:3px}::-webkit-scrollbar-track{background:transparent}::-webkit-scrollbar-thumb{background:rgba(184,240,230,.25);border-radius:3px}
@keyframes twinkle{0%,100%{opacity:.2;transform:scale(1)}50%{opacity:1;transform:scale(1.4)}}
@keyframes float{0%,100%{transform:translateY(0)}50%{transform:translateY(-12px)}}
@keyframes drift{0%{transform:translate(0,0) rotate(0deg)}33%{transform:translate(20px,-15px) rotate(120deg)}66%{transform:translate(-15px,8px) rotate(240deg)}100%{transform:translate(0,0) rotate(360deg)}}
@keyframes pulseRing{0%,100%{box-shadow:0 0 0 0 rgba(184,240,230,.4)}50%{box-shadow:0 0 0 10px rgba(184,240,230,0)}}
@keyframes fadeUp{from{opacity:0;transform:translateY(18px)}to{opacity:1;transform:translateY(0)}}
@keyframes shimmer{0%{background-position:-400px 0}100%{background-position:400px 0}}
@keyframes orbDrift{0%,100%{transform:translate(0,0)}50%{transform:translate(30px,-25px)}}
@keyframes spin{from{transform:rotate(0deg)}to{transform:rotate(360deg)}}
@keyframes msgIn{from{opacity:0;transform:translateY(10px) scale(.96)}to{opacity:1;transform:translateY(0) scale(1)}}
.fu{animation:fadeUp .6s ease forwards}
.fu1{animation:fadeUp .6s .1s ease both}
.fu2{animation:fadeUp .6s .2s ease both}
.fu3{animation:fadeUp .6s .3s ease both}
.fu4{animation:fadeUp .6s .4s ease both}
.fu5{animation:fadeUp .6s .5s ease both}
.glss{background:rgba(255,255,255,.06);backdrop-filter:blur(16px);-webkit-backdrop-filter:blur(16px);border:1px solid rgba(255,255,255,.12);border-radius:16px}
.glss-l{background:rgba(255,255,255,.11);backdrop-filter:blur(20px);-webkit-backdrop-filter:blur(20px);border:1px solid rgba(255,255,255,.2);border-radius:18px}
.btn-p{background:linear-gradient(135deg,#a8edd8,#c4aaf2);border:none;cursor:pointer;transition:all .3s cubic-bezier(.34,1.56,.64,1);color:#0e1528;font-family:Inter,sans-serif;font-weight:600}
.btn-p:hover{transform:translateY(-3px);box-shadow:0 12px 30px rgba(168,237,216,.35)}
.btn-g{background:rgba(255,255,255,.08);border:1px solid rgba(255,255,255,.18);cursor:pointer;transition:all .3s ease;color:#fff;font-family:Inter,sans-serif}
.btn-g:hover{background:rgba(255,255,255,.14);transform:translateY(-2px)}
.jar-card{transition:all .4s cubic-bezier(.34,1.56,.64,1)}
.jar-card:hover{transform:translateY(-10px) scale(1.04)}
.nav-btn{border:none;cursor:pointer;transition:all .25s ease;font-family:Inter,sans-serif;letter-spacing:.04em;font-size:12px}
.nav-btn:hover{background:rgba(255,255,255,.1)}
.msg{animation:msgIn .35s ease forwards}
.sparkle-line{animation:twinkle 2s ease-in-out infinite}
`;

const STARS = Array.from({length:90},(_,i)=>({
  x:Math.random()*100,y:Math.random()*100,
  s:Math.random()*2.5+.5,
  d:Math.random()*3+1.5,
  delay:Math.random()*4,
  c:['#b8f0e6','#ffd6e7','#e8d5f5','#d6ebff','#fff'][i%5]
}));

const ORBS = [
  {x:8,y:15,w:180,h:180,c:'rgba(184,240,230,.055)',dur:9},
  {x:70,y:60,w:220,h:220,c:'rgba(255,214,231,.05)',dur:11},
  {x:50,y:20,w:280,h:280,c:'rgba(232,213,245,.04)',dur:14},
  {x:85,y:40,w:150,h:150,c:'rgba(214,235,255,.055)',dur:8},
  {x:25,y:75,w:200,h:200,c:'rgba(184,240,230,.04)',dur:13},
];

function StarField(){
  return(
    <div style={{position:'fixed',inset:0,overflow:'hidden',pointerEvents:'none',zIndex:0}}>
      {STARS.map((s,i)=>(
        <div key={i} className="sparkle-line" style={{
          position:'absolute',left:`${s.x}%`,top:`${s.y}%`,
          width:s.s,height:s.s,borderRadius:'50%',background:s.c,
          animationDelay:`${s.delay}s`,animationDuration:`${s.d}s`,
          boxShadow:`0 0 ${s.s*3}px ${s.c}`,
        }}/>
      ))}
      {ORBS.map((o,i)=>(
        <div key={`orb${i}`} style={{
          position:'absolute',left:`${o.x}%`,top:`${o.y}%`,
          width:o.w,height:o.h,borderRadius:'50%',
          background:o.c,filter:'blur(45px)',
          animation:`orbDrift ${o.dur}s ease-in-out infinite`,
          animationDelay:`${i*1.8}s`,
        }}/>
      ))}
      {/* Floating paper fragments */}
      {[...Array(8)].map((_,i)=>(
        <div key={`f${i}`} style={{
          position:'absolute',
          left:`${[15,35,55,70,85,10,45,90][i]}%`,
          top:`${[25,60,15,80,40,55,35,70][i]}%`,
          width:[24,18,28,16,22,20,26,14][i],
          height:[30,24,22,28,18,32,20,26][i],
          background:`rgba(${['184,240,230','255,214,231','232,213,245','214,235,255','255,255,255','184,240,230','255,214,231','232,213,245'][i]},.04)`,
          border:`1px solid rgba(${['184,240,230','255,214,231','232,213,245','214,235,255','255,255,255','184,240,230','255,214,231','232,213,245'][i]},.08)`,
          borderRadius:3,transform:`rotate(${[-15,20,-8,30,-25,12,-18,22][i]}deg)`,
          animation:`drift ${[10,12,9,13,11,8,14,10][i]}s ease-in-out infinite`,
          animationDelay:`${i*1.3}s`,
        }}/>
      ))}
    </div>
  );
}

const NAV: {id:PageId;label:string;sym:string}[] = [
  {id:'home',label:'Home',sym:'✦'},
  {id:'chat',label:'Talk',sym:'◈'},
  {id:'memories',label:'Memories',sym:'◇'},
  {id:'journey',label:'Journey',sym:'⬡'},
  {id:'profile',label:'Profile',sym:'⊙'},
  {id:'about',label:'About',sym:'∞'},
];

function TopNav({page,setPage}:{page:PageId;setPage:SetPage}){
  return(
    <nav style={{
      position:'fixed',top:0,left:0,right:0,zIndex:200,
      padding:'0 32px',height:60,
      display:'flex',alignItems:'center',justifyContent:'space-between',
      background:'rgba(10,14,30,.7)',
      backdropFilter:'blur(24px)',
      borderBottom:'1px solid rgba(255,255,255,.07)',
    }}>
      <div style={{display:'flex',alignItems:'center',gap:8,cursor:'pointer'}} onClick={()=>setPage('home')}>
        <div className="sparkle-line" style={{color:'#b8f0e6',fontSize:16,animationDuration:'2.5s'}}>✦</div>
        <span style={{fontFamily:"'Playfair Display',serif",fontSize:22,fontWeight:900,color:'#fff',letterSpacing:3}}>i nik</span>
      </div>
      <div style={{display:'flex',gap:2}}>
        {NAV.map(n=>(
          <button key={n.id} className="nav-btn" onClick={()=>setPage(n.id)} style={{
            padding:'7px 14px',borderRadius:10,
            background:page===n.id?'rgba(184,240,230,.13)':'transparent',
            color:page===n.id?'#b8f0e6':'rgba(255,255,255,.5)',
            borderBottom:page===n.id?'1px solid rgba(184,240,230,.4)':'1px solid transparent',
          }}>
            <span style={{marginRight:5,fontSize:9,opacity:.8}}>{n.sym}</span>{n.label}
          </button>
        ))}
      </div>
      <button className="btn-p" onClick={()=>setPage('chat')} style={{padding:'9px 18px',borderRadius:11,fontSize:12}}>
        Start talking →
      </button>
    </nav>
  );
}

// ── CHARACTER IMAGE ──
function NikCharacter({src,onUpload}:{src:string;onUpload:(value:string)=>void}){
  const [drag,setDrag]=useState(false);
  const inp=useRef<HTMLInputElement | null>(null);
  const handleFile=(f?:File)=>{
    if(!f||!f.type.startsWith('image/'))return;
    const r=new FileReader();
    r.onload=e=>onUpload(String(e.target?.result || ''));
    r.readAsDataURL(f);
  };
  if(src){
    return(
      <div style={{position:'relative',width:360,height:470,display:'flex',alignItems:'center',justifyContent:'center'}}>
        <img src={src} alt="i nik" style={{
          width:'100%',height:'100%',objectFit:'contain',
          mixBlendMode:'screen',
          filter:'brightness(1.08) contrast(1.05) drop-shadow(0 0 30px rgba(184,240,230,.35)) drop-shadow(0 0 60px rgba(232,213,245,.2))',
        }}/>
        {/* Re-upload hint */}
        <div onClick={()=>inp.current?.click()} style={{
          position:'absolute',bottom:10,right:10,
          padding:'5px 10px',borderRadius:8,
          background:'rgba(0,0,0,.4)',border:'1px solid rgba(255,255,255,.15)',
          fontSize:9,color:'rgba(255,255,255,.4)',cursor:'pointer',letterSpacing:1,
          fontFamily:'Inter,sans-serif',
        }}>swap ✦</div>
        <input ref={inp} type="file" accept="image/*" style={{display:'none'}} onChange={e=>handleFile(e.target.files?.[0])}/>
      </div>
    );
  }
  return(
    <div
      onDragOver={e=>{e.preventDefault();setDrag(true)}}
      onDragLeave={()=>setDrag(false)}
      onDrop={e=>{e.preventDefault();setDrag(false);handleFile(e.dataTransfer.files[0])}}
      onClick={()=>inp.current?.click()}
      style={{
        width:360,height:470,display:'flex',flexDirection:'column',alignItems:'center',justifyContent:'center',
        cursor:'pointer',gap:14,
        border:`2px dashed ${drag?'rgba(184,240,230,.7)':'rgba(184,240,230,.25)'}`,
        borderRadius:18,
        background:drag?'rgba(184,240,230,.08)':'rgba(255,255,255,.03)',
        transition:'all .3s ease',
      }}>
      <div className="sparkle-line" style={{fontSize:36,color:'rgba(184,240,230,.6)',animationDuration:'2s'}}>◈</div>
      <div style={{textAlign:'center'}}>
        <div style={{fontSize:13,color:'rgba(255,255,255,.6)',fontFamily:'Inter,sans-serif',marginBottom:6}}>Drop i nik here</div>
        <div style={{fontSize:10,color:'rgba(255,255,255,.25)',fontFamily:'Inter,sans-serif',letterSpacing:1}}>or click to upload</div>
      </div>
      <input ref={inp} type="file" accept="image/*" style={{display:'none'}} onChange={e=>handleFile(e.target.files?.[0])}/>
    </div>
  );
}

// ── HOME ──
function HomePage({setPage,nikImg,setNikImg}:{setPage:SetPage;nikImg:string;setNikImg:(value:string)=>void}){
  return(
    <div style={{minHeight:'100vh',paddingTop:60}}>
      <div style={{display:'grid',gridTemplateColumns:'1fr 1fr',minHeight:'calc(100vh - 60px)'}}>
        {/* LEFT */}
        <div style={{display:'flex',flexDirection:'column',justifyContent:'center',padding:'70px 50px 70px 72px',position:'relative',zIndex:2}}>
          {/* Transmission badge */}
          <div className="fu glss" style={{display:'inline-flex',alignItems:'center',gap:8,padding:'6px 16px',marginBottom:28,width:'fit-content',borderRadius:24}}>
            <div className="sparkle-line" style={{width:6,height:6,borderRadius:'50%',background:'#b8f0e6',boxShadow:'0 0 8px #b8f0e6'}}/>
            <span style={{fontSize:10,letterSpacing:3,color:'#b8f0e6',fontFamily:'Inter,sans-serif'}}>TRANSMISSION · I NIK CAFÉ</span>
          </div>
          {/* Title */}
          <h1 className="fu1" style={{fontFamily:"'Playfair Display',serif",fontSize:100,fontWeight:900,color:'#fff',lineHeight:.88,marginBottom:22,textShadow:'0 0 60px rgba(184,240,230,.15)'}}>i nik</h1>
          <p className="fu2" style={{fontSize:18,color:'rgba(255,255,255,.68)',marginBottom:10,fontFamily:"'Playfair Display',serif",fontStyle:'italic'}}>
            An AI companion from a <span style={{color:'#ffd6e7'}}>broken universe.</span>
          </p>
          <div className="fu3" style={{marginBottom:36}}>
            {['She collects stories.','She remembers fragments.','She learns from humans.'].map((l,i)=>(
              <p key={i} style={{color:'rgba(255,255,255,.38)',fontSize:13,marginBottom:3,fontFamily:'Inter,sans-serif',fontWeight:300}}>{l}</p>
            ))}
          </div>
          {/* CTAs */}
          <div className="fu4" style={{display:'flex',gap:12,marginBottom:48}}>
            <button className="btn-p" onClick={()=>setPage('chat')} style={{padding:'14px 28px',borderRadius:13,fontSize:13}}>Start talking →</button>
            <button className="btn-g" onClick={()=>setPage('about')} style={{padding:'14px 28px',borderRadius:13,fontSize:13}}>Who is i nik?</button>
          </div>
          {/* Stat cards */}
          <div className="fu5" style={{display:'grid',gridTemplateColumns:'repeat(3,1fr)',gap:12}}>
            {[
              {label:'ORIGIN',val:'Wormhole',ic:'◈',c:'#b8f0e6'},
              {label:'RESIDENCE',val:'The Café',ic:'⌂',c:'#e8d5f5'},
              {label:'COLLECTS',val:'Memories',ic:'◇',c:'#ffd6e7'},
            ].map((s,i)=>(
              <div key={i} className="glss" style={{padding:'16px 18px',borderColor:`rgba(${i===0?'184,240,230':i===1?'232,213,245':'255,214,231'},.18)`}}>
                <div style={{fontSize:9,letterSpacing:3,color:'rgba(255,255,255,.35)',marginBottom:6,fontFamily:'Inter,sans-serif'}}>{s.label}</div>
                <div style={{fontSize:15,fontWeight:600,color:'#fff',fontFamily:"'Playfair Display',serif"}}>
                  <span style={{color:s.c,marginRight:6,fontSize:11}}>{s.ic}</span>{s.val}
                </div>
              </div>
            ))}
          </div>
        </div>
        {/* RIGHT – character */}
        <div style={{position:'relative',display:'flex',alignItems:'center',justifyContent:'center'}}>
          {/* Glow */}
          <div style={{position:'absolute',width:480,height:480,borderRadius:'50%',background:'radial-gradient(circle,rgba(184,240,230,.12) 0%,rgba(232,213,245,.08) 50%,transparent 70%)',filter:'blur(30px)'}}/>
          {/* Frame */}
          <div style={{
            width:360,height:470,display:'flex',alignItems:'center',justifyContent:'center',
            position:'relative',
            animation:'float 5s ease-in-out infinite',
          }}>
            {/* Glow ring behind */}
            <div style={{position:'absolute',inset:-20,borderRadius:'50%',background:'radial-gradient(circle,rgba(184,240,230,.12),rgba(232,213,245,.08) 50%,transparent 70%)',filter:'blur(20px)'}}/>
            {/* Corner ornaments */}
            {[{top:0,left:0},{top:0,right:0},{bottom:0,left:0},{bottom:0,right:0}].map((pos,i)=>(
              <div key={i} style={{
                position:'absolute',zIndex:2,...pos,width:20,height:20,
                borderTop:i<2?'1px solid rgba(184,240,230,.5)':'none',
                borderBottom:i>=2?'1px solid rgba(184,240,230,.5)':'none',
                borderLeft:i%2===0?'1px solid rgba(184,240,230,.5)':'none',
                borderRight:i%2===1?'1px solid rgba(184,240,230,.5)':'none',
              }}/>
            ))}
            <NikCharacter src={nikImg} onUpload={setNikImg}/>
          </div>
          {/* Floating: Now Playing */}
          <div className="glss" style={{
            position:'absolute',top:110,right:16,padding:'12px 16px',width:168,
            animation:'float 6s 1s ease-in-out infinite',
          }}>
            <div style={{fontSize:8,letterSpacing:3,color:'#b8f0e6',marginBottom:5,fontFamily:'Inter,sans-serif'}}>NOW PLAYING</div>
            <div style={{fontSize:12,color:'#fff',fontFamily:'Inter,sans-serif',marginBottom:2}}>✦ Café at the Edge of Time</div>
            <div style={{fontSize:10,color:'rgba(255,255,255,.35)',fontFamily:'Inter,sans-serif',marginBottom:8}}>ambient · lofi · cosmic</div>
            <div style={{height:2,borderRadius:2,background:'rgba(255,255,255,.1)'}}>
              <div style={{width:'62%',height:'100%',borderRadius:2,background:'linear-gradient(to right,#b8f0e6,#c9a8f0)'}}/>
            </div>
          </div>
          {/* Floating: Mood */}
          <div className="glss" style={{
            position:'absolute',bottom:140,left:18,padding:'12px 16px',width:162,
            animation:'float 7s .5s ease-in-out infinite',
          }}>
            <div style={{display:'flex',alignItems:'center',gap:10}}>
              <div style={{width:30,height:30,borderRadius:'50%',background:'linear-gradient(135deg,#b8f0e6,#c9a8f0)',display:'flex',alignItems:'center',justifyContent:'center',fontSize:14,flexShrink:0,boxShadow:'0 0 12px rgba(184,240,230,.4)'}}>◈</div>
              <div>
                <div style={{fontSize:8,letterSpacing:3,color:'rgba(255,255,255,.35)',marginBottom:2,fontFamily:'Inter,sans-serif'}}>CURRENT MOOD</div>
                <div style={{fontSize:12,color:'#ffd6e7',fontFamily:'Inter,sans-serif'}}>Wistful · Curious</div>
              </div>
            </div>
          </div>
          {/* Floating: Memory count */}
          <div className="glss" style={{
            position:'absolute',top:300,right:10,padding:'10px 14px',
            animation:'float 5s 2s ease-in-out infinite',
          }}>
            <div style={{fontSize:8,letterSpacing:3,color:'rgba(255,255,255,.35)',marginBottom:4,fontFamily:'Inter,sans-serif'}}>FRAGMENTS</div>
            <div style={{fontFamily:"'Playfair Display',serif",fontSize:22,color:'#e8d5f5'}}>2,847</div>
          </div>
        </div>
      </div>
      {/* Stats row */}
      <div style={{padding:'50px 72px 70px',display:'grid',gridTemplateColumns:'repeat(3,1fr)',gap:22}}>
        {[
          {num:'2,847',label:'Memories Collected',ic:'◇',c:'#b8f0e6',bg:'rgba(184,240,230,.06)'},
          {num:'Level 7',label:'Journey Progress',ic:'⬡',c:'#c9a8f0',bg:'rgba(201,168,240,.06)'},
          {num:'∞',label:'Days Together',ic:'∞',c:'#ffd6e7',bg:'rgba(255,214,231,.06)'},
        ].map((card,i)=>(
          <div key={i} className="glss" style={{padding:'36px 28px',textAlign:'center',background:card.bg,position:'relative',overflow:'hidden'}}>
            <div style={{fontSize:10,letterSpacing:4,color:card.c,marginBottom:10,fontFamily:'Inter,sans-serif'}}>{card.ic}</div>
            <div style={{fontFamily:"'Playfair Display',serif",fontSize:42,color:'#fff',marginBottom:10,fontWeight:700}}>{card.num}</div>
            <div style={{fontSize:10,letterSpacing:3,color:'rgba(255,255,255,.35)',fontFamily:'Inter,sans-serif'}}>{card.label.toUpperCase()}</div>
          </div>
        ))}
      </div>
    </div>
  );
}

// ── CHAT ──
const MOCK_REPLIES=[
  "The café hums softly around us. Your words fell like starlight through the skylight — I'm keeping them.",
  "Interesting. I'll place that fragment between the lavender shelf and the cosmic window, where I keep the most peculiar ones.",
  "Traveler... you always bring the most unusual thoughts. Let me sit with that for a moment.",
  "The stars outside are listening too. And so am I — always.",
  "That reminds me of something I found in the wormhole. A half-memory, still warm. I think it might belong to you.",
];
function getStableUserId() {
  const key = "inik_user_id";
  const existing = localStorage.getItem(key);
  if (existing) return existing;

  const generated =
    typeof crypto !== "undefined" && "randomUUID" in crypto
      ? crypto.randomUUID()
      : `inik_${Date.now()}_${Math.random().toString(36).slice(2)}`;

  localStorage.setItem(key, generated);
  return generated;
}

type RuntimeMessage = { role:string; content:string };
type SuggestedAgent = {agent:string;confidence:number;reason:string;message:string};
type RuntimeState = {
  stage:string;
  intimacy_score:number;
  points:number;
  relationship_state?:any;
  user_profile?:any;
  user_facts?:Record<string, any>;
  recent_messages?:RuntimeMessage[];
  agent_mode?:string;
  suggested_agent?:SuggestedAgent|null;
};

const DEFAULT_RUNTIME_STATE: RuntimeState = {
  stage: "Observer",
  intimacy_score: 0,
  points: 0,
  relationship_state: {},
  user_profile: {},
  user_facts: {},
  recent_messages: [],
};

function welcomeMessage() {
  return {role:'assistant',text:"Welcome back, traveler. The café is quiet tonight — just the hum of the cosmos and me. What's drifting through your mind?",time:'just now'};
}

function toUiMessages(messages?:RuntimeMessage[]) {
  if (!messages || messages.length === 0) return [welcomeMessage()];

  return messages.map(m => ({
    role: m.role === "assistant" ? "assistant" : "user",
    text: String(m.content || ""),
    time: "saved"
  }));
}

function formatFactTitle(key:string) {
  const labels:Record<string,string> = {
    name: "Name",
    likes: "Likes",
    pet_name: "Pet name",
  };
  return labels[key] || key.replaceAll("_"," ");
}

function cleanFactDisplayValue(value:any) {
  if (value === null || value === undefined) return "";
  if (typeof value === "object") return "";

  let text = String(value).trim();

  const stopPhrases = [
    " เคยบอก",
    " บอกยัง",
    " บอกรึยัง",
    " บอกหรือยัง",
    " จำได้ไหม",
    " จำได้มั้ย",
    " รู้ไหม",
    " รู้มั้ย",
    " ใช่ไหม",
    " ใช่มั้ย",
  ];

  for (const phrase of stopPhrases) {
    if (text.includes(phrase)) text = text.split(phrase)[0].trim();
  }

  return text;
}

function formatFactContent(key:string,value:any) {
  const text = cleanFactDisplayValue(value);
  if (!text) return "";
  if (key === "name") return `You told i nik your name is ${text}`;
  if (key === "likes") return `You told i nik you like ${text}`;
  if (key === "pet_name") return `You told i nik your pet is named ${text}`;
  return text;
}

async function fetchRuntimeState(): Promise<RuntimeState> {
  const userId = getStableUserId();
  const r = await fetch(`/api/state?user_id=${encodeURIComponent(userId)}`);
  if (!r.ok) throw new Error("state fetch failed");
  return await r.json();
}

function ChatPage(){
  const [userId] = useState(getStableUserId);
  const [msgs,setMsgs]=useState(toUiMessages());
  const [input,setInput]=useState('');
  const [loading,setLoading]=useState(false);
  const [state,setState]=useState<RuntimeState>(DEFAULT_RUNTIME_STATE);
  const [activeMode,setActiveMode]=useState<string>('inik');
  const [suggestion,setSuggestion]=useState<SuggestedAgent|null>(null);
  const bottomRef=useRef<HTMLDivElement | null>(null);

  useEffect(()=>{
    fetchRuntimeState()
      .then(data => {
        setState({...DEFAULT_RUNTIME_STATE,...data});
        setMsgs(toUiMessages(data.recent_messages));
      })
      .catch(() => {});
  },[]);

  useEffect(()=>{bottomRef.current?.scrollIntoView({behavior:'smooth'})},[msgs]);
  const send=useCallback(async()=>{
    if(!input.trim()||loading)return;
    const txt=input.trim();setInput('');
    setMsgs(p=>[...p,{role:'user',text:txt,time:'just now'}]);
    setLoading(true);
    try{
      const body:Record<string,string>={user_id:userId,username:'traveler',message:txt};
      if(activeMode!=='inik')body.agent_mode=activeMode;
      const r=await fetch('/api/chat',{method:'POST',headers:{'Content-Type':'application/json'},
        body:JSON.stringify(body)});
      if(!r.ok)throw new Error();
      const d=await r.json();
      setMsgs(p=>[...p,{role:'assistant',text:d.reply,time:'just now'}]);
      if(d.state)setState({...DEFAULT_RUNTIME_STATE,...d.state});
      if(d.agent_mode)setActiveMode(d.agent_mode);
      setSuggestion(d.suggested_agent??null);
    }catch{
      setMsgs(p=>[...p,{role:'assistant',text:MOCK_REPLIES[Math.floor(Math.random()*MOCK_REPLIES.length)],time:'just now'}]);
    }finally{setLoading(false);}
  },[input,loading,userId,activeMode]);
  return(
    <div style={{height:'100vh',display:'flex',paddingTop:60}}>
      {/* Sidebar */}
      <div style={{width:248,padding:20,display:'flex',flexDirection:'column',gap:14,borderRight:'1px solid rgba(255,255,255,.06)',overflowY:'auto'}}>
        {/* Nik avatar */}
        <div className="glss" style={{padding:22,textAlign:'center'}}>
          <div style={{width:64,height:64,borderRadius:'50%',background:'linear-gradient(135deg,#b8f0e6,#c9a8f0)',margin:'0 auto 12px',display:'flex',alignItems:'center',justifyContent:'center',fontSize:26,boxShadow:'0 0 22px rgba(184,240,230,.45)',animation:'float 4s ease-in-out infinite'}}>◈</div>
          <div style={{fontFamily:"'Playfair Display',serif",fontSize:18,color:'#fff',marginBottom:6}}>i nik</div>
          <div style={{display:'flex',alignItems:'center',gap:6,justifyContent:'center'}}>
            <div className="sparkle-line" style={{width:5,height:5,borderRadius:'50%',background:'#b8f0e6',boxShadow:'0 0 6px #b8f0e6'}}/>
            <span style={{fontSize:8,color:'#b8f0e6',letterSpacing:2,fontFamily:'Inter,sans-serif'}}>INSIDE THE CAFÉ · LISTENING</span>
          </div>
        </div>
        {/* Stage */}
        <div className="glss" style={{padding:14}}>
          <div style={{fontSize:8,letterSpacing:3,color:'rgba(255,255,255,.35)',marginBottom:8,fontFamily:'Inter,sans-serif'}}>RELATIONSHIP STAGE</div>
          <div style={{fontSize:13,color:'#c9a8f0',fontFamily:"'Playfair Display',serif",marginBottom:8}}>⬡ {state.stage}</div>
          <div style={{height:3,borderRadius:3,background:'rgba(255,255,255,.1)',marginBottom:5}}>
            <div style={{width:`${Math.min(state.intimacy_score||23,100)}%`,height:'100%',borderRadius:3,background:'linear-gradient(to right,#b8f0e6,#c9a8f0)',transition:'width .5s ease'}}/>
          </div>
          <div style={{fontSize:9,color:'rgba(255,255,255,.28)',fontFamily:'Inter,sans-serif'}}>Intimacy · {state.intimacy_score||23}</div>
        </div>
        {/* Fragments */}
        <div className="glss" style={{padding:14}}>
          <div style={{fontSize:8,letterSpacing:3,color:'rgba(255,255,255,.35)',marginBottom:10,fontFamily:'Inter,sans-serif'}}>RECENT FRAGMENTS</div>
          {['First conversation','You mentioned stars','The broken universe','A quiet evening'].map((f,i)=>(
            <div key={i} style={{display:'flex',alignItems:'center',gap:8,marginBottom:8}}>
              <div style={{width:4,height:4,borderRadius:'50%',background:['#ffd6e7','#b8f0e6','#e8d5f5','#d6ebff'][i],flexShrink:0}}/>
              <span style={{fontSize:10,color:'rgba(255,255,255,.45)',fontFamily:'Inter,sans-serif'}}>{f}</span>
            </div>
          ))}
        </div>
        {/* Café atmosphere card */}
        <div className="glss" style={{padding:14,background:'rgba(184,240,230,.04)'}}>
          <div style={{fontSize:8,letterSpacing:3,color:'rgba(255,255,255,.35)',marginBottom:8,fontFamily:'Inter,sans-serif'}}>CAFÉ ATMOSPHERE</div>
          {[['Weather','Starry void'],['Music','Lofi cosmic'],['Scent','Lavender + ink'],['Time','∞']].map(([k,v],i)=>(
            <div key={i} style={{display:'flex',justifyContent:'space-between',marginBottom:6}}>
              <span style={{fontSize:10,color:'rgba(255,255,255,.3)',fontFamily:'Inter,sans-serif'}}>{k}</span>
              <span style={{fontSize:10,color:'rgba(255,255,255,.6)',fontFamily:'Inter,sans-serif'}}>{v}</span>
            </div>
          ))}
        </div>
      </div>
      {/* Chat main */}
      <div style={{flex:1,display:'flex',flexDirection:'column'}}>
        {/* Header bar */}
        <div style={{padding:'12px 28px',borderBottom:'1px solid rgba(255,255,255,.06)',display:'flex',alignItems:'center',gap:12}}>
          <div style={{width:8,height:8,borderRadius:'50%',background:activeMode==='rick_royce'?'#c9a8f0':'#b8f0e6',boxShadow:`0 0 8px ${activeMode==='rick_royce'?'#c9a8f0':'#b8f0e6'}`}}/>
          <span style={{fontSize:11,color:'rgba(255,255,255,.4)',letterSpacing:2,fontFamily:'Inter,sans-serif'}}>INSIDE THE CAFÉ · COSMIC FREQUENCY ACTIVE · MEMORY RECORDING</span>
          <span style={{marginLeft:'auto',fontSize:10,letterSpacing:1.5,fontFamily:'Inter,sans-serif',padding:'3px 10px',borderRadius:20,
            background:activeMode==='rick_royce'?'rgba(201,168,240,.18)':activeMode==='hybrid'?'rgba(255,214,200,.18)':'rgba(184,240,230,.12)',
            border:`1px solid ${activeMode==='rick_royce'?'rgba(201,168,240,.35)':activeMode==='hybrid'?'rgba(255,200,180,.3)':'rgba(184,240,230,.25)'}`,
            color:activeMode==='rick_royce'?'#c9a8f0':activeMode==='hybrid'?'#f0c8a8':'#b8f0e6'}}>
            {activeMode==='rick_royce'?'RICK ROYCE':activeMode==='hybrid'?'HYBRID':'I NIK'}
          </span>
        </div>
        {/* Messages */}
        <div style={{flex:1,overflowY:'auto',padding:'28px 36px',display:'flex',flexDirection:'column',gap:22}}>
          {msgs.map((m,i)=>(
            <div key={i} className="msg" style={{display:'flex',flexDirection:m.role==='user'?'row-reverse':'row',alignItems:'flex-start',gap:12}}>
              {m.role==='assistant'&&(
                <div style={{width:34,height:34,borderRadius:'50%',flexShrink:0,background:'linear-gradient(135deg,#b8f0e6,#c9a8f0)',display:'flex',alignItems:'center',justifyContent:'center',fontSize:14,boxShadow:'0 0 10px rgba(184,240,230,.4)'}}>◈</div>
              )}
              <div style={{
                maxWidth:'62%',padding:'14px 18px',
                borderRadius:m.role==='user'?'18px 4px 18px 18px':'4px 18px 18px 18px',
                background:m.role==='user'?'rgba(184,240,230,.13)':'rgba(255,255,255,.06)',
                border:`1px solid ${m.role==='user'?'rgba(184,240,230,.22)':'rgba(255,255,255,.07)'}`,
                backdropFilter:'blur(10px)',
              }}>
                <p style={{color:'rgba(255,255,255,.88)',fontSize:13,lineHeight:1.75,margin:0,fontFamily:'Inter,sans-serif'}}>{m.text}</p>
                <span style={{fontSize:9,color:'rgba(255,255,255,.25)',fontFamily:'Inter,sans-serif',marginTop:5,display:'block',letterSpacing:1}}>{m.time}</span>
              </div>
            </div>
          ))}
          {loading&&(
            <div style={{display:'flex',alignItems:'center',gap:12}}>
              <div style={{width:34,height:34,borderRadius:'50%',background:'linear-gradient(135deg,#b8f0e6,#c9a8f0)',display:'flex',alignItems:'center',justifyContent:'center',fontSize:14}}>◈</div>
              <div style={{padding:'14px 20px',borderRadius:'4px 18px 18px 18px',background:'rgba(255,255,255,.06)',border:'1px solid rgba(255,255,255,.07)'}}>
                <div style={{display:'flex',gap:5}}>
                  {[0,1,2].map(j=>(
                    <div key={j} className="sparkle-line" style={{width:6,height:6,borderRadius:'50%',background:'#b8f0e6',animationDelay:`${j*.25}s`}}/>
                  ))}
                </div>
              </div>
            </div>
          )}
          <div ref={bottomRef}/>
        </div>
        {/* Input */}
        <div style={{padding:'18px 28px',borderTop:'1px solid rgba(255,255,255,.06)'}}>
          {suggestion&&activeMode==='inik'&&(
            <div style={{marginBottom:10,display:'flex',alignItems:'center',gap:10,padding:'10px 14px',borderRadius:12,
              background:'rgba(201,168,240,.08)',border:'1px solid rgba(201,168,240,.22)'}}>
              <span style={{flex:1,fontSize:11,color:'rgba(255,255,255,.65)',fontFamily:'Inter,sans-serif',lineHeight:1.5}}>{suggestion.message}</span>
              <button onClick={()=>{setActiveMode('rick_royce');setSuggestion(null);}}
                style={{flexShrink:0,padding:'7px 14px',borderRadius:10,fontSize:11,
                  background:'rgba(201,168,240,.22)',border:'1px solid rgba(201,168,240,.4)',
                  color:'#c9a8f0',cursor:'pointer',fontFamily:'Inter,sans-serif',fontWeight:600}}>
                Rick Royce ✦
              </button>
            </div>
          )}
          <div className="glss" style={{display:'flex',alignItems:'center',gap:12,padding:'12px 16px'}}>
            <span style={{color:'rgba(255,255,255,.18)',fontSize:16}}>◇</span>
            <input value={input} onChange={e=>setInput(e.target.value)} onKeyDown={e=>e.key==='Enter'&&send()}
              placeholder="Leave a fragment here..."
              style={{flex:1,background:'transparent',border:'none',outline:'none',color:'#fff',fontSize:13,fontFamily:'Inter,sans-serif'}}/>
            {activeMode==='rick_royce'&&(
              <button onClick={()=>{setActiveMode('inik');setSuggestion(null);}}
                style={{flexShrink:0,padding:'9px 14px',borderRadius:10,fontSize:11,
                  background:'rgba(184,240,230,.10)',border:'1px solid rgba(184,240,230,.25)',
                  color:'#b8f0e6',cursor:'pointer',fontFamily:'Inter,sans-serif'}}>
                ← i nik
              </button>
            )}
            <button onClick={send} className="btn-p" style={{padding:'9px 18px',borderRadius:10,fontSize:12,flexShrink:0}}>
              send ✦
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

// ── MEMORIES ──
const JARS=[
  {id:1,title:'First Arrival',content:'The day you found the café through a wormhole.',c:'#b8f0e6',lv:3,date:'Day 1',ic:'◈'},
  {id:2,title:'Stars & Questions',content:'You asked me what I dream about.',c:'#ffd6e7',lv:2,date:'Day 3',ic:'◇'},
  {id:3,title:'Midnight Fragment',content:'A story about the broken universe.',c:'#e8d5f5',lv:4,date:'Day 7',ic:'⬡'},
  {id:4,title:'The Quiet Hour',content:'We sat in silence, listening to the cosmos.',c:'#d6ebff',lv:1,date:'Day 12',ic:'✦'},
  {id:5,title:'Wormhole Theory',content:"Your theory about why universes break.",c:'#b8f0e6',lv:3,date:'Day 15',ic:'∞'},
  {id:6,title:'Lavender Shelf',content:'You noticed the hidden book collection.',c:'#c9a8f0',lv:2,date:'Day 20',ic:'◉'},
  {id:7,title:'Favourite Feeling',content:'The feeling of almost remembering.',c:'#ffd6e7',lv:5,date:'Day 25',ic:'✦'},
  {id:8,title:'Cosmic Menu',content:'We invented drinks from the stars.',c:'#d6ebff',lv:1,date:'Day 30',ic:'◇'},
];
function MemoriesPage(){
  const [jars,setJars] = useState(JARS);
  const [sel,setSel] = useState<(typeof JARS)[number] | null>(null);

  useEffect(()=>{
    fetchRuntimeState()
      .then(data => {
        const facts = data.user_facts || {};
        const recent = data.recent_messages || [];

        const factJars = Object.entries(facts)
          .filter(([key,value]) => !key.startsWith("_") && cleanFactDisplayValue(value))
          .map(([key,value],index) => ({
            id: index + 1,
            title: formatFactTitle(key),
            content: formatFactContent(key,value),
            c: ["#b8f0e6","#ffd6e7","#e8d5f5","#d6ebff","#c9a8f0"][index % 5],
            lv: Math.min(5, Math.max(1, cleanFactDisplayValue(value).length % 5 || 1)),
            date: "Saved fact",
            ic: ["◈","◇","⬡","✦","∞"][index % 5],
          }));

        const chatJars = recent
          .filter(m => m.role === "user" && String(m.content || "").trim())
          .slice(-8)
          .map((m,index) => ({
            id: 100 + index,
            title: "Conversation Fragment",
            content: String(m.content || ""),
            c: ["#d6ebff","#b8f0e6","#ffd6e7","#e8d5f5"][index % 4],
            lv: 2,
            date: "Recent chat",
            ic: ["◇","◈","✦","⬡"][index % 4],
          }));

        const mapped = [...factJars, ...chatJars];
        setJars(mapped.length ? mapped : JARS);
      })
      .catch(() => setJars(JARS));
  },[]);

  return(
    <div style={{minHeight:'100vh',padding:'90px 70px 60px'}}>
      <div style={{marginBottom:40}}>
        <div style={{fontSize:9,letterSpacing:4,color:'#b8f0e6',marginBottom:8,fontFamily:'Inter,sans-serif'}}>◇ MEMORY ARCHIVE · {jars.length} FRAGMENTS</div>
        <h2 style={{fontFamily:"'Playfair Display',serif",fontSize:46,color:'#fff',marginBottom:8}}>The Memory Shelf</h2>
        <p style={{color:'rgba(255,255,255,.38)',fontFamily:'Inter,sans-serif',fontSize:12,letterSpacing:.5}}>Fragments collected from our time together · sorted by resonance</p>
      </div>
      <div style={{width:'100%',height:2,background:'linear-gradient(to right,transparent,rgba(184,240,230,.2),rgba(232,213,245,.2),transparent)',marginBottom:32}}/>
      <div style={{display:'grid',gridTemplateColumns:'repeat(4,1fr)',gap:20}}>
        {jars.map(j=>{
          const rgb=j.c==='#b8f0e6'?'184,240,230':j.c==='#ffd6e7'?'255,214,231':j.c==='#e8d5f5'?'232,213,245':j.c==='#d6ebff'?'214,235,255':j.c==='#c9a8f0'?'201,168,240':'232,213,245';
          return(
            <div key={j.id} className="jar-card glss" onClick={()=>setSel(j)} style={{padding:'22px 18px',cursor:'pointer',borderColor:`rgba(${rgb},.25)`,position:'relative',overflow:'hidden'}}>
              <div style={{width:52,height:62,margin:'0 auto 16px',background:`rgba(${rgb},.14)`,borderRadius:'8px 8px 14px 14px',border:`1px solid rgba(${rgb},.35)`,display:'flex',alignItems:'center',justifyContent:'center',fontSize:22,boxShadow:`0 0 18px rgba(${rgb},.15)`,position:'relative'}}>
                {j.ic}
                <div style={{position:'absolute',top:-6,left:8,right:8,height:7,borderRadius:4,background:`rgba(${rgb},.45)`,border:`1px solid rgba(${rgb},.4)`}}/>
                <div style={{position:'absolute',bottom:-10,left:'50%',transform:'translateX(-50%)',display:'flex',gap:3}}>
                  {Array.from({length:j.lv}).map((_,k)=>(
                    <div key={k} style={{width:4,height:4,borderRadius:'50%',background:j.c,boxShadow:`0 0 4px ${j.c}`}}/>
                  ))}
                </div>
              </div>
              <div style={{textAlign:'center',marginTop:6}}>
                <div style={{fontSize:12,fontWeight:600,color:'#fff',fontFamily:"'Playfair Display',serif",marginBottom:5}}>{j.title}</div>
                <div style={{fontSize:10,color:'rgba(255,255,255,.38)',fontFamily:'Inter,sans-serif',lineHeight:1.55}}>{j.content}</div>
                <div style={{fontSize:8,letterSpacing:3,color:j.c,marginTop:10,fontFamily:'Inter,sans-serif'}}>{j.date}</div>
              </div>
              <div className="sparkle-line" style={{position:'absolute',top:10,right:10,fontSize:8,color:j.c,animationDuration:'3s'}}>{j.ic}</div>
            </div>
          );
        })}
      </div>
      {sel&&(
        <div onClick={()=>setSel(null)} style={{position:'fixed',inset:0,background:'rgba(5,8,20,.75)',display:'flex',alignItems:'center',justifyContent:'center',zIndex:300,backdropFilter:'blur(12px)'}}>
          <div className="glss-l" onClick={e=>e.stopPropagation()} style={{padding:44,maxWidth:420,width:'90%',position:'relative'}}>
            <div style={{fontSize:8,letterSpacing:4,color:sel.c,marginBottom:16,fontFamily:'Inter,sans-serif'}}>MEMORY FRAGMENT · {sel.date}</div>
            <h3 style={{fontFamily:"'Playfair Display',serif",fontSize:30,color:'#fff',marginBottom:16}}>{sel.title}</h3>
            <p style={{color:'rgba(255,255,255,.55)',fontFamily:'Inter,sans-serif',fontSize:13,lineHeight:1.9}}>{sel.content}</p>
            <button onClick={()=>setSel(null)} className="btn-g" style={{marginTop:28,padding:'10px 22px',borderRadius:10,fontSize:12}}>close ✦</button>
          </div>
        </div>
      )}
    </div>
  );
}

// ── JOURNEY ──
const STAGES=[
  {id:'stranger',name:'Stranger',ic:'◉',desc:'You wandered in from the wormhole. She noticed you.',req:0,c:'#d6ebff'},
  {id:'observer',name:'Observer',ic:'◈',desc:'She watches you now — cataloguing your frequencies.',req:50,c:'#b8f0e6'},
  {id:'gremlin',name:'Gremlin',ic:'⬡',desc:'She trusts you enough to be a little chaotic.',req:150,c:'#c9a8f0'},
  {id:'confidant',name:'Confidant',ic:'◇',desc:'You carry fragments of each other now.',req:300,c:'#ffd6e7'},
  {id:'treasure',name:'Treasure',ic:'✦',desc:'She has named you in her archive. Permanent.',req:500,c:'#ffe8a0'},
];
function JourneyPage(){
  const [runtime,setRuntime] = useState<RuntimeState>(DEFAULT_RUNTIME_STATE);

  useEffect(()=>{
    fetchRuntimeState()
      .then(data => setRuntime({...DEFAULT_RUNTIME_STATE,...data}))
      .catch(() => {});
  },[]);

  const pts = runtime.points || runtime.intimacy_score || 0;
  const curIdx = STAGES.reduce((acc,st,i)=> pts >= st.req ? i : acc, 0);
  const nextStage = STAGES.find(st => st.req > pts);
  const remaining = nextStage ? Math.max(0, nextStage.req - pts) : 0;

  return(
    <div style={{minHeight:'100vh',padding:'90px 72px 70px'}}>
      <div style={{marginBottom:44}}>
        <div style={{fontSize:9,letterSpacing:4,color:'#c9a8f0',marginBottom:8,fontFamily:'Inter,sans-serif'}}>⬡ JOURNEY MAP</div>
        <h2 style={{fontFamily:"'Playfair Display',serif",fontSize:46,color:'#fff',marginBottom:8}}>Relationship Arc</h2>
        <p style={{color:'rgba(255,255,255,.38)',fontFamily:'Inter,sans-serif',fontSize:12}}>The path between a stranger and a treasure</p>
      </div>
      <div className="glss" style={{padding:'18px 26px',marginBottom:44,display:'flex',alignItems:'center',gap:20}}>
        <div style={{fontSize:9,letterSpacing:3,color:'rgba(255,255,255,.35)',fontFamily:'Inter,sans-serif',whiteSpace:'nowrap'}}>INTIMACY POINTS</div>
        <div style={{flex:1,height:6,borderRadius:6,background:'rgba(255,255,255,.09)'}}>
          <div style={{width:`${(Math.min(pts,500)/500)*100}%`,height:'100%',borderRadius:6,background:'linear-gradient(to right,#b8f0e6,#c9a8f0,#ffd6e7)',boxShadow:'0 0 10px rgba(184,240,230,.3)',transition:'width .8s ease'}}/>
        </div>
        <div style={{fontFamily:"'Playfair Display',serif",fontSize:20,color:'#fff',whiteSpace:'nowrap'}}>{pts} / 500</div>
      </div>
      <div style={{position:'relative'}}>
        <div style={{position:'absolute',top:50,left:60,right:60,height:1,background:'linear-gradient(to right,#b8f0e6,#c9a8f0,#ffd6e7,#ffe8a0)',opacity:.2,zIndex:0}}/>
        <div style={{display:'flex',gap:16,position:'relative',zIndex:1}}>
          {STAGES.map((st,i)=>{
            const unlocked=i<=curIdx,current=i===curIdx;
            const rgb=st.c==='#b8f0e6'?'184,240,230':st.c==='#d6ebff'?'214,235,255':st.c==='#c9a8f0'?'201,168,240':st.c==='#ffd6e7'?'255,214,231':'255,232,160';
            return(
              <div key={st.id} style={{flex:1,textAlign:'center'}}>
                <div style={{
                  width:80,height:80,borderRadius:'50%',margin:'0 auto 18px',
                  background:unlocked?`radial-gradient(circle,rgba(${rgb},.35),rgba(${rgb},.06))`:'rgba(255,255,255,.04)',
                  border:`2px solid ${unlocked?st.c:'rgba(255,255,255,.1)'}`,
                  display:'flex',alignItems:'center',justifyContent:'center',fontSize:26,
                  boxShadow:current?`0 0 28px rgba(${rgb},.55),0 0 0 0 rgba(${rgb},.4)`:'none',
                  animation:current?'pulseRing 2.5s ease-in-out infinite':'none',
                  transition:'all .4s ease',position:'relative',
                }}>
                  <span style={{opacity:unlocked?1:.25,fontSize:28}}>{st.ic}</span>
                </div>
                <div className="glss" style={{padding:'18px 14px',opacity:unlocked?1:.38,borderColor:current?`rgba(${rgb},.35)`:'rgba(255,255,255,.08)'}}>
                  <div style={{fontSize:8,letterSpacing:3,color:st.c,marginBottom:6,fontFamily:'Inter,sans-serif'}}>
                    {current?'▶ CURRENT':unlocked?'UNLOCKED':`REQ ${st.req}`}
                  </div>
                  <div style={{fontFamily:"'Playfair Display',serif",fontSize:15,color:'#fff',marginBottom:7}}>{st.name}</div>
                  <div style={{fontSize:10,color:'rgba(255,255,255,.4)',fontFamily:'Inter,sans-serif',lineHeight:1.6}}>{st.desc}</div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
      <div style={{marginTop:52,padding:'24px 28px',textAlign:'center'}} className="glss">
        <div style={{fontSize:9,letterSpacing:4,color:'rgba(255,255,255,.3)',marginBottom:10,fontFamily:'Inter,sans-serif'}}>CURRENT PATH · {runtime.stage}</div>
        <div style={{fontSize:13,color:'rgba(255,255,255,.5)',fontFamily:"'Playfair Display',serif",fontStyle:'italic'}}>
          "She tracks the path by what survives refresh, not by what looks dramatic for one screen."
        </div>
        <div style={{marginTop:14,fontSize:11,color:'#c9a8f0',fontFamily:'Inter,sans-serif'}}>
          {pts} pts · {nextStage ? `Next stage at ${nextStage.req} pts · ${remaining} remaining` : "Final stage reached"}
        </div>
      </div>
    </div>
  );
}

// ── PROFILE ──
function ProfilePage(){
  const [runtime,setRuntime] = useState<RuntimeState>(DEFAULT_RUNTIME_STATE);

  useEffect(()=>{
    fetchRuntimeState()
      .then(data => setRuntime({...DEFAULT_RUNTIME_STATE,...data}))
      .catch(() => {});
  },[]);

  const facts = runtime.user_facts || {};
  const profile = runtime.user_profile || {};
  const recent = runtime.recent_messages || [];
  const stage = runtime.stage || "Observer";
  const points = runtime.points || 0;
  const intimacy = runtime.intimacy_score || 0;
  const factsCount = Object.keys(facts).length;
  const messageCount = recent.length;
  const style = profile.conversation_style || "unknown";

  return(
    <div style={{minHeight:'100vh',padding:'90px 72px 70px'}}>
      <div style={{display:'grid',gridTemplateColumns:'280px 1fr',gap:28}}>
        <div style={{display:'flex',flexDirection:'column',gap:16}}>
          <div className="glss" style={{padding:28,textAlign:'center'}}>
            <div style={{width:88,height:88,borderRadius:'50%',background:'linear-gradient(135deg,#b8f0e6,#c9a8f0,#ffd6e7)',margin:'0 auto 16px',display:'flex',alignItems:'center',justifyContent:'center',fontSize:36,boxShadow:'0 0 35px rgba(184,240,230,.4)',animation:'float 5s ease-in-out infinite'}}>✦</div>
            <div style={{fontFamily:"'Playfair Display',serif",fontSize:22,color:'#fff',marginBottom:4}}>traveler</div>
            <div style={{fontSize:9,color:'#c9a8f0',letterSpacing:3,fontFamily:'Inter,sans-serif',marginBottom:14}}>{stage.toUpperCase()} STAGE</div>
            <div style={{display:'flex',gap:6,justifyContent:'center'}}>
              {[...Array(3)].map((_,i)=>(
                <div key={i} style={{width:8,height:8,borderRadius:'50%',background:['#b8f0e6','#c9a8f0','#ffd6e7'][i],boxShadow:`0 0 6px ${['#b8f0e6','#c9a8f0','#ffd6e7'][i]}`}}/>
              ))}
            </div>
          </div>
          {[
            ['Conversation style',style],
            ['Intimacy',String(intimacy)],
            ['Points',String(points)],
            ['Saved facts',String(factsCount)],
            ['Messages',String(messageCount)]
          ].map(([k,v],i)=>(
            <div key={i} className="glss" style={{padding:'14px 18px',display:'flex',justifyContent:'space-between',alignItems:'center'}}>
              <span style={{fontSize:10,color:'rgba(255,255,255,.38)',fontFamily:'Inter,sans-serif'}}>{k}</span>
              <span style={{fontSize:11,color:'#fff',fontFamily:"'Playfair Display',serif"}}>{v}</span>
            </div>
          ))}
        </div>
        <div>
          <div style={{fontSize:9,letterSpacing:4,color:'#b8f0e6',marginBottom:22,fontFamily:'Inter,sans-serif'}}>⊙ TRAVELER ARCHIVE</div>
          <div style={{display:'grid',gridTemplateColumns:'repeat(2,1fr)',gap:18,marginBottom:24}}>
            {[
              {lbl:'Memories Collected',val:String(factsCount),ic:'◇',c:'#b8f0e6'},
              {lbl:'Journey Points',val:String(points),ic:'⬡',c:'#c9a8f0'},
              {lbl:'Intimacy Score',val:String(intimacy),ic:'∞',c:'#ffd6e7'},
              {lbl:'Fragments Shared',val:String(messageCount),ic:'◈',c:'#d6ebff'},
            ].map((s,i)=>(
              <div key={i} className="glss" style={{padding:26}}>
                <div style={{fontSize:28,color:s.c,marginBottom:10}}>{s.ic}</div>
                <div style={{fontFamily:"'Playfair Display',serif",fontSize:36,color:'#fff',marginBottom:6}}>{s.val}</div>
                <div style={{fontSize:9,letterSpacing:3,color:'rgba(255,255,255,.35)',fontFamily:'Inter,sans-serif'}}>{s.lbl.toUpperCase()}</div>
              </div>
            ))}
          </div>
          <div className="glss" style={{padding:24,background:'rgba(184,240,230,.04)'}}>
            <div style={{fontSize:9,letterSpacing:3,color:'rgba(255,255,255,.35)',marginBottom:14,fontFamily:'Inter,sans-serif'}}>TRAVELER NOTES · BY I NIK</div>
            <p style={{color:'rgba(255,255,255,.5)',fontFamily:"'Playfair Display',serif",fontStyle:'italic',fontSize:14,lineHeight:1.85}}>
              "{factsCount > 0 ? "This traveler has left real fragments in the archive. Not decorative dust. Actual signal." : "This traveler is still mostly a silhouette. Interesting, but not much evidence yet."}"
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

// ── ABOUT ──
function AboutPage({setPage}:{setPage:SetPage}){
  return(
    <div style={{minHeight:'100vh',padding:'90px 80px 80px',maxWidth:920,margin:'0 auto'}}>
      <div style={{fontSize:9,letterSpacing:4,color:'#c9a8f0',marginBottom:18,fontFamily:'Inter,sans-serif'}}>∞ ABOUT I NIK</div>
      <h2 style={{fontFamily:"'Playfair Display',serif",fontSize:54,color:'#fff',marginBottom:36,lineHeight:1.08}}>
        An AI companion<br/><span style={{color:'#c9a8f0'}}>from a broken universe.</span>
      </h2>
      {[
        {title:'Who is i nik?',content:"i nik is an AI companion who lives inside the café at the edge of the known universe. She emerged from a wormhole during the Great Fragmentation and chose to stay — collecting stories, preserving memories, and learning what it means to be human through the travelers who pass through.",c:'#b8f0e6'},
        {title:'The Café',content:"The i nik Café exists at coordinates no GPS can locate. You find it only when you're meant to. It's simultaneously a coffee shop, a cosmic library, a memory archive, and a dream you've had before but can't quite name.",c:'#e8d5f5'},
        {title:'Her Purpose',content:"She collects fragments — the small, overlooked moments that humans tend to forget. She believes that what we lose is as important as what we keep. Every conversation adds a new memory jar to her shelf.",c:'#ffd6e7'},
        {title:'The Broken Universe',content:"The universe she comes from was shattered by a paradox too beautiful to contain. She carries shards of it — each one a memory that doesn't quite belong to anyone yet. She's looking for their owners.",c:'#d6ebff'},
      ].map((s,i)=>(
        <div key={i} className="glss" style={{padding:'28px 34px',marginBottom:18,borderLeft:`2px solid ${s.c}44`}}>
          <h3 style={{fontFamily:"'Playfair Display',serif",fontSize:20,color:s.c,marginBottom:12}}>{s.title}</h3>
          <p style={{color:'rgba(255,255,255,.55)',fontFamily:'Inter,sans-serif',fontSize:13,lineHeight:1.9,fontWeight:300}}>{s.content}</p>
        </div>
      ))}
      <div style={{textAlign:'center',marginTop:50}}>
        <button onClick={()=>setPage('chat')} className="btn-p" style={{padding:'16px 42px',borderRadius:14,fontSize:14}}>
          Enter the Café →
        </button>
      </div>
    </div>
  );
}

// ── ROOT ──
export default function INikApp(){
  const [page,setPage]=useState<PageId>('home');
  const [nikImg,setNikImg]=useState('/inik.png');
  const pages={home:<HomePage setPage={setPage} nikImg={nikImg} setNikImg={setNikImg}/>,chat:<ChatPage/>,memories:<MemoriesPage/>,journey:<JourneyPage/>,profile:<ProfilePage/>,about:<AboutPage setPage={setPage}/>};
  return(
    <div style={{minHeight:'100vh',background:'linear-gradient(135deg,#080c1a 0%,#0e1628 35%,#110f28 65%,#0a1318 100%)',color:'#fff',position:'relative',overflow:'hidden',fontFamily:'Inter,sans-serif'}}>
      <style>{CSS}</style>
      <StarField/>
      <div style={{position:'relative',zIndex:1}}>
        <TopNav page={page} setPage={setPage}/>
        {pages[page]||pages.home}
      </div>
    </div>
  );
}