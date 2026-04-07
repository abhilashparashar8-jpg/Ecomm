import React, { useEffect, useState } from 'react';
import api from '../api/axios';
import ProductCard from '../components/ProductCard';
import useStore from '../store/useStore';
import { useNavigate } from 'react-router-dom';

export default function Home() {
  const user = useStore(state => state.user);
  const activeProfile = useStore(state => state.activeProfile);
  const navigate = useNavigate();
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);

  const isKids = activeProfile?.isKids || false;
  const isDev = import.meta.env.VITE_APP_MODE === 'dev';

  // RESTORED ORIGINAL KIDS CONTENT (Animal/Cartoon)
  const KIDS_PRODUCTS = [
    { id: 101, name: "Funny Monkey Story", category: "Jungle Fun", youtube_id: "1w0I8F0yRvs", image_url: "https://images.unsplash.com/photo-1540573133985-87b6da6d54a9?w=800" },
    { id: 102, name: "The Lion King", category: "Learn with Animals", youtube_id: "7TavVZMewpY", image_url: "https://images.unsplash.com/photo-1546182990-dffeafbe841d?w=800" },
    { id: 103, name: "Forest Adventure", category: "Jungle Fun", youtube_id: "KYniUCGPGLs", image_url: "https://images.unsplash.com/photo-1441974231531-c6227db76b6e?w=800" },
    { id: 104, name: "Playful Tiger", category: "Jungle Fun", youtube_id: "t0Q2otsqC4I", image_url: "https://images.unsplash.com/photo-1508817628294-5a453fa0b8fb?w=800" },
    { id: 105, name: "Fun Farm Songs", category: "Baby Songs", youtube_id: "e_04ZrNroTo", image_url: "https://images.unsplash.com/photo-1500382017468-9049fed747ef?w=800" },
    { id: 106, name: "Zebra's Party", category: "Learn with Animals", youtube_id: "r1N7uS_BsvM", image_url: "https://images.unsplash.com/photo-1501705388883-4ed8a543392c?w=800" },
    { id: 107, name: "Baby Shark Dance", category: "Trending Now", youtube_id: "XqZsoesa55w", image_url: "https://images.unsplash.com/photo-1560275619-4662e366661b?w=800" },
    { id: 108, name: "Magical Forest", category: "Trending Now", youtube_id: "T-d-1Xo3jG4", image_url: "https://images.unsplash.com/photo-1511497584788-876760111969?w=800" },
  ];

  // ADULT MODE PUNEET CONTENT (MASTER CATALOG - FINAL ALIGNMENT)
  const DUMMY_PRODUCTS = [
    { id: 201, name: "Shararat (Dhurandhar)", category: "Action & Adventure", youtube_id: "YyepU5ztLf4", image_url: "https://img.youtube.com/vi/YyepU5ztLf4/hqdefault.jpg", description: "High-octane action featuring Ranveer Singh." },
    { id: 202, name: "Jaiye Sajana (Dhurandhar)", category: "Action & Adventure", youtube_id: "F2m4HPLvj-4", image_url: "https://img.youtube.com/vi/F2m4HPLvj-4/hqdefault.jpg", description: "Dhurandhar The Revenge - Musical High." },
    { id: 203, name: "Jaan Se Guzarte Hain", category: "Action & Adventure", youtube_id: "IAONd2d_PDU", image_url: "https://img.youtube.com/vi/IAONd2d_PDU/hqdefault.jpg", description: "Lyrical saga of Dhurandhar The Revenge." },
    { id: 204, name: "Dhurandhar (Full Album)", category: "Action & Adventure", youtube_id: "jo3p7O8n6is", image_url: "https://img.youtube.com/vi/jo3p7O8n6is/hqdefault.jpg", description: "The complete musical journey of a hero." },
    { id: 205, name: "Mohe Mor Banaiyo Radha", category: "Devotional & Soulful", youtube_id: "IzC6Cgqcup0", image_url: "https://img.youtube.com/vi/IzC6Cgqcup0/hqdefault.jpg", description: "Peaceful Radha Krishna Bhajan." },
    { id: 206, name: "Radhe Tere Charno Ki", category: "Devotional & Soulful", youtube_id: "lZQ5XzKrUFM", image_url: "https://img.youtube.com/vi/lZQ5XzKrUFM/hqdefault.jpg", description: "Soulful Radha Bhajan for inner peace." },
    { id: 207, name: "Samay Samjhayega (Sad)", category: "Devotional & Soulful", youtube_id: "6ZwwapPikyQ", image_url: "https://img.youtube.com/vi/6ZwwapPikyQ/hqdefault.jpg", description: "Tum Prem Ho Sad Version - Radha Krishn." },
    { id: 208, name: "Radha Apne Vrindavan Ko", category: "Devotional & Soulful", youtube_id: "zdVpB9m9GqI", image_url: "https://img.youtube.com/vi/zdVpB9m9GqI/hqdefault.jpg", description: "Another peaceful rendition of the Radha Bhajan." },
  ];

  useEffect(() => {
    // FORCE LOADING TIMEOUT: Always show content even if API fails or hangs
    const timer = setTimeout(() => {
      if (loading) {
        setProducts(isKids ? KIDS_PRODUCTS : DUMMY_PRODUCTS);
        setLoading(false);
      }
    }, 1500);

    const loadContent = async () => {
        if (!isKids) {
          try {
            // FOR PUNEET: We always want the Master Catalog for the 'WOW' factor
            // The backend shuffling is good, but we ensure names are STABLE
            const res = await api.get('/product/products');
            if (res.data && res.data.length > 0 && res.data[0].name !== "Stream Selection 1") {
              setProducts(res.data);
            } else {
              setProducts(DUMMY_PRODUCTS);
            }
          } catch (err) {
            setProducts(DUMMY_PRODUCTS);
          }
        } else {
           setProducts(KIDS_PRODUCTS);
        }
        setLoading(false);
        clearTimeout(timer);
    };

    loadContent();
    return () => clearTimeout(timer);
  }, [isKids]);

  const groupedProducts = (products.length > 0 ? products : (isKids ? KIDS_PRODUCTS : DUMMY_PRODUCTS)).reduce((acc, p) => {
    const cat = p.category || 'Trending Now';
    acc[cat] = acc[cat] || [];
    acc[cat].push(p);
    return acc;
  }, {});

  // For Hero: Adults pick from Adult list, Kids pick from STABLE Kids list
  const kidsHeroPool = [
    { name: "Big Buck Bunny", youtube_id: "aqz-KE-bpKQ", description: "A giant rabbit takes revenge on some bullying rodents." },
    { name: "Spring", youtube_id: "WhWc3b3KhnY", description: "A shepherd girl and her dog face ancient spirits to continue the cycle of life." }
  ];

  const heroSource = isKids ? kidsHeroPool : DUMMY_PRODUCTS;
  const randomHeroVideo = heroSource[Math.floor(Math.random() * heroSource.length)];

  const heroData = {
      title: randomHeroVideo.name,
      video_id: randomHeroVideo.youtube_id,
      desc: randomHeroVideo.description || "A spectacular feature presentation from StreamShop catálogo.",
      badge: isKids ? "FAMILY FAVORITE" : "STREAMSHOP CHOICE"
  };

  return (
    <div className={`relative min-h-screen ${isKids ? 'bg-[#1a0a2e]' : 'bg-[#141414]'} overflow-hidden transition-colors duration-1000`}>
       {/* Hero Section */}
       <div className="relative h-screen w-full overflow-hidden z-0">
         <div className={`absolute inset-0 z-20 ${isKids ? 'bg-gradient-to-t from-[#1a0a2e] via-transparent to-pink-500/20' : 'bg-gradient-to-t from-[#141414] via-[#141414]/20 to-black/60'}`} />
         <div className={`absolute inset-0 z-20 ${isKids ? 'bg-gradient-to-r from-purple-900/40 via-transparent to-transparent' : 'bg-gradient-to-r from-black/80 via-transparent to-transparent'}`} />
         
         <div className="absolute inset-0 w-full h-full z-10 pointer-events-none overflow-hidden scale-[1.2]">
            <iframe 
              key={heroData.video_id}
              src={`https://www.youtube.com/embed/${heroData.video_id}?autoplay=1&mute=1&controls=0&start=30&loop=1&playlist=${heroData.video_id}&iv_load_policy=3&disablekb=1&fs=0&modestbranding=1`}
              allow="autoplay; encrypted-media; gyroscope; picture-in-picture"
              className="w-full h-full animate-[kenburns_40s_ease_infinite_alternate]" 
              frameBorder="0"
            />
         </div>

         <style dangerouslySetInnerHTML={{ __html: `
            @keyframes kenburns {
                0% { transform: scale(1); }
                100% { transform: scale(1.15) translate(-1%, -1%); }
            }
         `}} />
       </div>

       {/* Hero Content Overlay */}
       <div className="absolute top-0 left-0 w-full h-screen z-20 pointer-events-none">
         <div className="absolute bottom-0 left-[4%] pb-32 w-full max-w-2xl animate-fade-in-up pointer-events-auto">
            <div className="flex items-center gap-2 mb-2">
                {isKids ? (
                   <span className="bg-yellow-400 text-purple-900 px-3 py-1 rounded-full font-black text-xs tracking-tighter shadow-lg transform -rotate-3">{heroData.badge}</span>
                ) : (
                  <>
                    <img src="https://upload.wikimedia.org/wikipedia/commons/0/08/Netflix_2015_logo.svg" className="h-6" style={{filter: 'invert(16%) sepia(87%) saturate(5833%) hue-rotate(352deg) brightness(97%) contrast(116%)'}} alt="N" />
                    <h2 className="text-sm text-neutral-300 font-bold tracking-[0.25em]">S E R I E S</h2>
                  </>
                )}
            </div>
            <h1 className="text-4xl font-black text-white drop-shadow-2xl mb-4 leading-tight tracking-tight uppercase">
               {heroData.title}
            </h1>
            <p className="text-base text-white font-medium drop-shadow-lg mb-8 max-w-lg line-clamp-3 text-neutral-200">
              {heroData.desc}
            </p>
            <div className="flex space-x-4">
              <button 
                onClick={() => user ? alert("Playing Awesome Content!") : navigate('/login')}
                className={`${isKids ? 'bg-yellow-400 text-purple-900 hover:bg-yellow-300' : 'bg-white text-black hover:bg-neutral-300'} px-8 py-2.5 rounded font-bold transition-all duration-300 flex items-center gap-3 text-lg transform hover:scale-105`}
              >
                 <svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="currentColor"><path d="M8 5v14l11-7z"/></svg>
                 Play
              </button>
              <button className={`${isKids ? 'bg-purple-600/50 hover:bg-purple-600/70' : 'bg-neutral-500/50 hover:bg-neutral-500/70'} backdrop-blur-md text-white px-8 py-2.5 rounded font-bold transition-all duration-300 flex items-center gap-3 text-lg transform hover:scale-105`}>
                 <svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>
                 More Info
              </button>
            </div>
         </div>
       </div>

       {/* Movie Rows */}
       <div className="z-10 relative -mt-32 pb-20 space-y-12">
         {!loading ? (
             Object.entries(groupedProducts).map(([category, items], rowIndex) => (
                <div key={category} className="px-[4%] group">
                   <h2 className={`text-xl md:text-2xl font-bold mb-4 tracking-wide group-hover:text-white transition-colors ${isKids ? 'text-yellow-400' : 'text-neutral-200'}`}>{category}</h2>
                   <div className="flex overflow-x-visible gap-2 md:gap-4 pb-16 pt-4 no-scrollbar snap-x relative z-30">
                        {items.map((product, idx) => (
                          <div className="min-w-[160px] md:min-w-[280px] snap-start relative transition-all duration-500 cursor-pointer" key={product.id + category + idx}>
                             {rowIndex === 0 && (
                                 <div className={`${isKids ? 'bg-yellow-400 text-purple-900 border-yellow-200' : 'bg-[#E50914] text-white border-red-400/30'} absolute -top-3 -right-3 z-[60] font-black text-[10px] px-2 py-1.5 rounded shadow-lg border flex flex-col items-center`}>
                                     <span className="leading-none opacity-80 uppercase tracking-tighter">{isKids ? 'FUN' : 'TOP'}</span>
                                     <span className="text-lg leading-none mt-0.5">{idx + 1}</span>
                                 </div>
                             )}
                             <ProductCard product={product} index={idx} />
                          </div>
                        ))}
                   </div>
                </div>
             ))
         ) : (
            <div className="px-[4%]">
               <h2 className="text-2xl font-bold mb-4 bg-neutral-800 w-48 h-8 rounded animate-pulse"></h2>
               <div className="flex gap-4 pb-4 overflow-hidden">
                  {Array(6).fill().map((_, i) => (
                    <div key={i} className="min-w-[160px] md:min-w-[280px] bg-neutral-800 animate-pulse h-40 rounded-md shadow-lg border border-neutral-800">
                    </div>
                  ))}
               </div>
            </div>
         )}
       </div>
    </div>
  );
}
