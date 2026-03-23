import React, { useState, useEffect, useRef } from 'react';
import { 
  Cpu, Zap, ShieldAlert, Activity,
  Terminal as TerminalIcon, Search, AlertTriangle, Crosshair,
  FileText, CheckSquare, Square, X, Download, TrendingUp, TrendingDown
} from 'lucide-react';

const API_BASE_URL = 'http://127.0.0.1:8080';

export default function App() {
  const [targetUrl, setTargetUrl] = useState('');
  const [intercepts, setIntercepts] = useState([]);
  const [selectedIds, setSelectedIds] = useState([]);
  const [isScanning, setIsScanning] = useState(false);
  const [entropy, setEntropy] = useState(0.1);
  const [status, setStatus] = useState('SOVEREIGN_IDLE');
  const [isComparing, setIsComparing] = useState(false);

  // Chromatic Entropy Mapping
  useEffect(() => {
    const hue = 210 - (entropy * 165); // Shifting from Blue (210) to Amber (45)
    document.body.style.backgroundColor = `hsl(${hue}, 60%, 5%)`;
    document.body.style.transition = 'background-color 1.5s ease-in-out';
  }, [entropy]);

  const handleIntercept = async (e) => {
    if (e) e.preventDefault();
    if (!targetUrl.trim()) return;

    setIsScanning(true);
    setStatus('BYPASSING_BOT_LAYERS');
    setEntropy(0.4);

    try {
      const urls = targetUrl.split(',').map(u => u.trim()).filter(u => u);
      
      let data;
      if (urls.length > 1) {
        const response = await fetch(`${API_BASE_URL}/api/v1/batch_intercept`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(urls.map(url => ({ url })))
        });
        if (!response.ok) throw new Error('BATCH_BYPASS_FAILED');
        data = await response.json();
      } else {
        const response = await fetch(`${API_BASE_URL}/api/v1/intercept`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ url: urls[0] })
        });
        if (!response.ok) throw new Error('CORE_BYPASS_FAILED');
        data = await response.json();
      }
      
      setIntercepts(prev => [...data, ...prev]);
      setEntropy(0.9);
      setStatus('OMNI_SYNCHRONIZED');
    } catch (err) {
      setStatus('INTERCEPT_FAILED');
      setEntropy(0.2);
    } finally {
      setIsScanning(false);
    }
  };

  const toggleSelect = (id) => {
    setSelectedIds(prev =>
      prev.includes(id) ? prev.filter(i => i !== id) : [...prev, id]
    );
  };

  const generateReport = () => {
    const selectedData = intercepts.filter(i => selectedIds.includes(i.id));
    const reportText = `NEXUS OMNI FORENSIC REPORT - ${new Date().toLocaleString()}\n` +
      "=".repeat(50) + "\n\n" +
      selectedData.map(i =>
        `TARGET: ${i.title}\nID: ${i.id}\nSHADOW PRICE: ${i.shadow_price.toLocaleString()} OMR\nMAX BID: ${i.max_bid.toLocaleString()} OMR\nROI: ${i.roi_percentage.toFixed(2)}%\nENTROPY: ${i.entropy_level}\n${"-".repeat(20)}`
      ).join("\n\n");

    const blob = new Blob([reportText], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `nexus_forensic_report_${Date.now()}.txt`;
    a.click();
  };

  const selectedData = intercepts.filter(i => selectedIds.includes(i.id));
  const maxRoi = Math.max(...selectedData.map(i => i.roi_percentage), 0);

  return (
    <div className="min-h-screen text-slate-400 font-mono p-8 selection:bg-blue-500 selection:text-white">
      
      {/* Sovereign Header */}
      <header className="max-w-6xl mx-auto flex items-center justify-between mb-16 border-b border-slate-800 pb-8">
        <div className="flex items-center gap-4">
          <div className="p-3 bg-slate-900 border border-slate-700 rounded-sm">
            <TerminalIcon size={24} className="text-blue-400" />
          </div>
          <div>
            <h1 className="text-2xl font-black tracking-tighter text-white uppercase italic">Nexus Omni</h1>
            <p className="text-[10px] text-slate-500 tracking-[0.3em] font-bold">SOVEREIGN_INTERCEPTOR_V1.2</p>
          </div>
        </div>

        <div className="flex items-center gap-8">
          {selectedIds.length > 0 && (
            <div className="flex gap-4">
              <button
                onClick={() => setIsComparing(true)}
                className="px-4 py-2 bg-indigo-600 text-white text-[10px] font-black uppercase tracking-widest hover:bg-white hover:text-black transition-all shadow-[0_0_15px_rgba(79,70,229,0.4)]"
              >
                COMPARE ({selectedIds.length})
              </button>
              <button
                onClick={generateReport}
                className="px-4 py-2 border border-slate-700 text-[10px] font-black uppercase tracking-widest hover:bg-slate-700 hover:text-white transition-all flex items-center gap-2"
              >
                <Download size={12} /> REPORT
              </button>
            </div>
          )}
          <div className="text-right">
            <p className="text-[10px] text-slate-600 font-bold uppercase mb-1">Entropy State</p>
            <div className="w-32 h-1 bg-slate-800 rounded-full overflow-hidden">
              <div
                className="h-full bg-blue-500 transition-all duration-1000"
                style={{ width: `${entropy * 100}%`, backgroundColor: entropy > 0.7 ? '#fbbf24' : '#3b82f6' }}
              />
            </div>
          </div>
          <div className="px-4 py-2 bg-slate-900 border border-slate-800 rounded text-[10px] font-bold text-emerald-500 animate-pulse">
            {status}
          </div>
        </div>
      </header>

      {/* Control Throttle */}
      <main className="max-w-4xl mx-auto">
        <div className="mb-20">
          <form onSubmit={handleIntercept} className="relative group">
            <div className="absolute -inset-0.5 bg-gradient-to-r from-blue-500 to-amber-500 rounded-lg blur opacity-20 group-hover:opacity-40 transition duration-1000"></div>
            <div className="relative flex bg-black border border-slate-800 rounded-lg overflow-hidden">
              <div className="p-4 flex items-center justify-center border-r border-slate-800">
                <Search size={20} className="text-slate-600" />
              </div>
              <input 
                type="text" 
                placeholder="INPUT_MARKET_URL(S) (comma separated for batch scan)..."
                className="flex-1 bg-transparent border-none p-6 text-sm text-white focus:ring-0 placeholder:text-slate-700"
                value={targetUrl}
                onChange={(e) => setTargetUrl(e.target.value)}
              />
              <button
                type="submit"
                disabled={isScanning}
                className="px-10 bg-slate-900 text-white text-[11px] font-black uppercase tracking-widest hover:bg-white hover:text-black transition-all border-l border-slate-800 disabled:opacity-50"
              >
                {isScanning ? 'SHADOW_FETCHING...' : 'INITIATE_SNIPE'}
              </button>
            </div>
          </form>
        </div>

        {/* Action-First Heatmap/List */}
        <div className="space-y-4">
          {intercepts.map(item => (
            <div key={item.id} className="group relative bg-slate-950 border border-slate-900 p-6 rounded-lg hover:border-slate-700 transition-all overflow-hidden">
              <div className="flex items-center justify-between relative z-10">
                <div className="flex items-center gap-6">
                  <button
                    onClick={() => toggleSelect(item.id)}
                    className="p-2 hover:text-blue-400 transition-colors"
                  >
                    {selectedIds.includes(item.id) ? <CheckSquare size={20} className="text-blue-500" /> : <Square size={20} />}
                  </button>
                  <div className="p-4 bg-black border border-slate-800 rounded flex items-center justify-center">
                    <Crosshair size={24} className={item.entropy_level > 0.8 ? "text-amber-500" : "text-blue-500"} />
                  </div>
                  <div>
                    <h3 className="text-white font-bold text-lg tracking-tight mb-1 italic">{item.title}</h3>
                    <div className="flex items-center gap-4 text-[10px] font-bold text-slate-600">
                      <span className="flex items-center gap-1"><Cpu size={12} /> {item.id}</span>
                      <span className="flex items-center gap-1"><Activity size={12} /> MOMENTUM: {item.momentum}</span>
                    </div>
                  </div>
                </div>

                <div className="text-right">
                  <div className="text-[10px] text-slate-600 font-bold uppercase mb-1">Shadow Price</div>
                  <div className="text-2xl font-black text-white tracking-tighter italic">
                    {item.shadow_price.toLocaleString()} <span className="text-xs text-slate-500 not-italic">OMR</span>
                  </div>
                </div>

                <div className="flex gap-4 ml-12">
                  <button className="px-6 py-3 border border-slate-800 text-[10px] font-black uppercase tracking-widest hover:bg-rose-500 hover:text-white hover:border-rose-500 transition-all">
                    SHRED
                  </button>
                  <button className="px-8 py-3 bg-blue-600 text-white text-[10px] font-black uppercase tracking-widest hover:bg-white hover:text-black transition-all shadow-[0_0_15px_rgba(37,99,235,0.3)]">
                    LOCK_INTERCEPT
                  </button>
                </div>
              </div>

              {/* Kinetic Shadow Background */}
              <div
                className="absolute inset-y-0 left-0 bg-gradient-to-r from-blue-500/5 to-transparent transition-all duration-1000"
                style={{ width: `${item.entropy_level * 100}%` }}
              />
            </div>
          ))}

          {intercepts.length === 0 && !isScanning && (
            <div className="py-20 text-center border border-dashed border-slate-800 rounded-lg">
              <AlertTriangle className="mx-auto text-slate-800 mb-4" size={48} />
              <p className="text-[10px] text-slate-700 font-black uppercase tracking-widest">Awaiting Command Input</p>
            </div>
          )}
        </div>
      </main>

      {/* Comparison Modal */}
      {isComparing && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-8 bg-black/90 backdrop-blur-sm">
          <div className="bg-slate-900 border border-slate-800 rounded-lg w-full max-w-6xl max-h-[90vh] overflow-hidden flex flex-col shadow-[0_0_50px_rgba(0,0,0,0.8)]">
            <div className="p-6 border-b border-slate-800 flex justify-between items-center bg-slate-950">
              <div className="flex items-center gap-4">
                <h2 className="text-xl font-black uppercase italic text-white tracking-tighter">Forensic Comparison Heatmap</h2>
                <div className="flex items-center gap-2 px-3 py-1 bg-emerald-500/10 border border-emerald-500/20 rounded-full">
                  <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
                  <span className="text-[8px] font-bold text-emerald-500 uppercase">Live Deals Active</span>
                </div>
              </div>
              <button onClick={() => setIsComparing(false)} className="p-2 hover:bg-slate-800 rounded-full transition-colors">
                <X size={24} />
              </button>
            </div>
            <div className="flex-1 overflow-x-auto p-6 bg-slate-900/50">
              <div className="flex gap-6 min-w-max">
                {selectedData.map(item => {
                  const isBestRoi = item.roi_percentage === maxRoi && maxRoi > 0;
                  return (
                    <div key={item.id} className={`w-80 bg-slate-950 border ${isBestRoi ? 'border-emerald-500/50 shadow-[0_0_30px_rgba(16,185,129,0.1)]' : 'border-slate-800'} rounded-lg p-6 space-y-6 relative overflow-hidden transition-all duration-500`}>
                      {isBestRoi && (
                        <div className="absolute top-0 right-0 bg-emerald-500 text-black text-[8px] font-black px-4 py-1 uppercase tracking-tighter rotate-45 translate-x-3 translate-y-2">
                          Best Alpha
                        </div>
                      )}
                      <div className="space-y-2">
                        <div className="text-[10px] text-slate-600 font-bold uppercase">Target Identity</div>
                        <h4 className="text-white font-bold text-lg italic truncate">{item.title}</h4>
                        <div className="text-[10px] text-blue-500 font-bold flex items-center gap-2">
                          #{item.id}
                          {item.roi_percentage > 15 ? <TrendingUp size={12} className="text-emerald-500" /> : <TrendingDown size={12} className="text-rose-500" />}
                        </div>
                      </div>
                      <div className="grid grid-cols-2 gap-4">
                        <div className="p-3 bg-black border border-slate-900 rounded">
                          <div className="text-[8px] text-slate-600 font-bold uppercase mb-1">Shadow Price</div>
                          <div className="text-sm font-black text-white">{item.shadow_price.toLocaleString()}</div>
                        </div>
                        <div className="p-3 bg-black border border-slate-900 rounded">
                          <div className="text-[8px] text-slate-600 font-bold uppercase mb-1">Max Bid</div>
                          <div className="text-sm font-black text-emerald-500">{item.max_bid.toLocaleString()}</div>
                        </div>
                        <div className="p-3 bg-black border border-slate-900 rounded relative overflow-hidden">
                          <div className="text-[8px] text-slate-600 font-bold uppercase mb-1">ROI Est.</div>
                          <div className={`text-sm font-black ${item.roi_percentage > 15 ? 'text-emerald-500' : 'text-blue-500'}`}>
                            {item.roi_percentage.toFixed(1)}%
                          </div>
                          <div className="absolute bottom-0 left-0 h-0.5 bg-blue-500" style={{ width: `${item.roi_percentage}%` }} />
                        </div>
                        <div className="p-3 bg-black border border-slate-900 rounded">
                          <div className="text-[8px] text-slate-600 font-bold uppercase mb-1">Entropy</div>
                          <div className="text-sm font-black text-amber-500">{item.entropy_level}</div>
                        </div>
                      </div>
                      <div className="space-y-2">
                        <div className="text-[10px] text-slate-600 font-bold uppercase">Forensic Summary</div>
                        <p className="text-[10px] leading-relaxed text-slate-400">
                          System synchronized at ${new Date(item.timestamp * 1000).toLocaleTimeString()}.
                          High momentum detected with ${item.momentum} volatility rating.
                          Recommended intercept strategy: ${item.roi_percentage > 20 ? 'AGGRESSIVE SNIPE' : 'PATIENT ENTRY'}.
                        </p>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Biometric Status Overlay */}
      <footer className="fixed bottom-8 left-8 right-8 flex items-center justify-between text-[9px] font-bold text-slate-700 uppercase tracking-widest">
        <div className="flex items-center gap-6">
          <span className="flex items-center gap-2"><div className="w-1.5 h-1.5 rounded-full bg-emerald-500" /> RUST_CORE_ACTIVE</span>
          <span className="flex items-center gap-2"><div className="w-1.5 h-1.5 rounded-full bg-blue-500" /> H2_TLS_MORPHING</span>
          <span className="flex items-center gap-2 text-blue-400 animate-pulse"><FileText size={10} /> {selectedIds.length} ENTITIES SELECTED</span>
        </div>
        <div>
          LATENCY: 0.42MS // OMAN_REGION_ACTIVE // SYSTEM_ENTITY: SOVEREIGN_ARCHITECT
        </div>
      </footer>
    </div>
  );
}
