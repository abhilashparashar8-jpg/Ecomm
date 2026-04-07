import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../api/axios';
import useStore from '../store/useStore';

export default function ProductDetails() {
  const { id } = useParams();
  const navigate = useNavigate();
  const user = useStore(state => state.user);
  
  const [product, setProduct] = useState(null);
  const [reviews, setReviews] = useState([]);
  const [loading, setLoading] = useState(true);
  const [newReviewText, setNewReviewText] = useState('');
  const [rating, setRating] = useState(5);

  // RESTORED KIDS CONTENT (Animal/Cartoon)
  const KIDS_PRODUCTS = [
    { id: 101, name: "Big Buck Bunny", category: "Jungle Fun", youtube_id: "aqz-KE-bpKQ", image_url: "https://images.unsplash.com/photo-1540573133985-87b6da6d54a9?w=800" },
    { id: 102, name: "Spring", category: "Learn with Animals", youtube_id: "WhWc3b3KhnY", image_url: "https://images.unsplash.com/photo-1546182990-dffeafbe841d?w=800" },
    { id: 103, name: "Sintel", category: "Jungle Fun", youtube_id: "eRsGyueVLvQ", image_url: "https://images.unsplash.com/photo-1441974231531-c6227db76b6e?w=800" },
    { id: 104, name: "Agent 327", category: "Jungle Fun", youtube_id: "mN0zPOpADL4", image_url: "https://images.unsplash.com/photo-1508817628294-5a453fa0b8fb?w=800" },
    { id: 105, name: "Caminandes 1", category: "Baby Songs", youtube_id: "SkVqJ1SGoEI", image_url: "https://images.unsplash.com/photo-1500382017468-9049fed747ef?w=800" },
    { id: 106, name: "Caminandes 2", category: "Learn with Animals", youtube_id: "Z4C82eyhwxc", image_url: "https://images.unsplash.com/photo-1501705388883-4ed8a543392c?w=800" },
    { id: 107, name: "Cosmos", category: "Trending Now", youtube_id: "Y-rmzh0PI3c", image_url: "https://images.unsplash.com/photo-1560275619-4662e366661b?w=800" },
    { id: 108, name: "Glass Half", category: "Trending Now", youtube_id: "W0mEA3p9w2k", image_url: "https://images.unsplash.com/photo-1511497584788-876760111969?w=800" },
  ];

  // MASTER CATALOG (STRICTLY MATCHED)
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
    fetchData();
  }, [id]);

  const fetchData = async () => {
    try {
      const idx = parseInt(id) || 0;
      let prodRes = null;
      let revRes = null;
      
      try {
          prodRes = await api.get(`/product/products/${id}`);
      } catch (err) {
          const allProds = [...KIDS_PRODUCTS, ...DUMMY_PRODUCTS];
          const match = allProds.find(p => p.id === idx);
          if (match) {
            prodRes = { data: { ...match, price: 19.99, stock: 100 } };
          } else {
            prodRes = { data: { ...DUMMY_PRODUCTS[0], id: idx } };
          }
      }

      try {
          revRes = await api.get(`/review/reviews/product/${id}`);
      } catch(err) { revRes = { data: [] }; }

      setProduct(prodRes.data);
      setReviews(revRes.data);
    } catch (err) {
      console.error("Failed to fetch details", err);
    } finally {
      setLoading(false);
    }
  };

  const submitReview = async (e) => {
    e.preventDefault();
    if (!user) return navigate('/login');
    try {
      await api.post('/review/reviews', {
        product_id: parseInt(id),
        rating: rating,
        comment: newReviewText
      });
      setNewReviewText('');
      fetchData(); // reload reviews
    } catch (err) {
      console.error(err);
      alert('Failed to submit review');
    }
  };

  if (loading) return <div className="min-h-screen bg-[#141414] text-white flex justify-center items-center font-bold text-xl animate-pulse">Loading StreamShop Feature...</div>;
  if (!product) return <div className="min-h-screen bg-[#141414] text-white flex justify-center items-center">Title not found in StreamShop Catalog.</div>;

  const videoId = product.youtube_id || 'YyepU5ztLf4';

  return (
    <div className="bg-[#141414] min-h-screen text-white pt-16">
       {/* Cinematic Player Section */}
       <div className="w-full bg-black aspect-video relative shadow-2xl border-b border-zinc-800 group overflow-hidden">
           {user ? (
               <iframe 
                 className="w-full h-full scale-[1.01]"
                 src={`https://www.youtube.com/embed/${videoId}?autoplay=1&mute=0&controls=1&showinfo=0&rel=0&modestbranding=1&iv_load_policy=3`} 
                 title={product.name} 
                 allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" 
                 allowFullScreen
               />
           ) : (
               <div className="w-full h-full flex flex-col items-center justify-center bg-zinc-900 border-b border-zinc-800 p-8 text-center bg-cover bg-center" style={{backgroundImage: `linear-gradient(rgba(0,0,0,0.8), rgba(0,0,0,0.8)), url(${product.image_url})`}}>
                  <h2 className="text-4xl font-black mb-4 drop-shadow-lg">Stream Authentication Required</h2>
                  <p className="text-gray-300 mb-8 max-w-md text-lg">You must sign in to watch full features and premium previews.</p>
                  <button onClick={() => navigate('/login')} className="bg-white text-black px-12 py-4 rounded-md font-black text-lg hover:bg-neutral-200 transition-all transform hover:scale-105 active:scale-95 shadow-xl">Sign In to Stream Now</button>
               </div>
           )}
       </div>

       {/* Movie / Product Details */}
       <div className="max-w-6xl mx-auto p-10 grid grid-cols-1 md:grid-cols-3 gap-16">
            <div className="md:col-span-2 space-y-8 animate-fade-in">
                <div>
                   <h1 className="text-6xl font-black mb-4 drop-shadow-2xl tracking-tighter leading-none">{product.name}</h1>
                   <div className="flex items-center gap-6 text-sm font-bold">
                        <span className="text-green-500 text-lg">99% Match</span>
                        <span className="text-neutral-400">2024</span>
                        <span className="border border-neutral-600 px-2 py-0.5 rounded-sm text-neutral-300">ULTRA HD 4K</span>
                        <span className="text-zinc-500 uppercase tracking-widest">{product.category || 'Streaming'}</span>
                    </div>
                </div>

                <p className="text-xl text-neutral-300 leading-relaxed font-medium">{product.description || "A spectacular feature presentation from StreamShop catálogo."}</p>
                
                <div className="flex items-center gap-4">
                    <button className="bg-white text-black font-black px-10 py-3 rounded flex items-center gap-3 hover:bg-neutral-200 transition transform hover:scale-105 active:scale-95 shadow-lg">
                         <svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="currentColor"><path d="M8 5v14l11-7z"/></svg>
                         Watch Feature
                    </button>
                </div>
            </div>

            {/* Sidebar */}
            <div className="bg-neutral-900/40 border border-neutral-800 p-8 rounded-xl h-min shadow-2xl flex flex-col space-y-6 backdrop-blur-sm">
                <div className="relative group overflow-hidden rounded-md shadow-2xl border border-neutral-700">
                   <img className="w-full object-cover" src={product.image_url} alt={product.name} />
                </div>
                <div>
                   <h4 className="font-black text-5xl text-white mb-1 tracking-tighter">${product.price}</h4>
                   <p className="text-xs text-green-500 font-black uppercase tracking-tight">PREMIUM STREAM ACCESS</p>
                </div>
                <button 
                  onClick={async () => {
                      if (!user) return navigate('/login');
                      await api.post('/cart/cart', { product_id: product.id, quantity: 1 });
                      alert('Added to cart!');
                  }}
                  className="w-full bg-red-600 text-white font-black py-4 rounded hover:bg-red-700 transition"
                >
                  ADD TO WATCHLIST
                </button>
            </div>
       </div>
    </div>
  );
}
