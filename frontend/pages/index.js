import React , {useState , useEffect} from 'react';
import axios from 'axios';

function HomePage() {

    const [data, setData] = useState("Loading...");

    useEffect(()=>{
        axios.get("http://localhost:3001/")
        .then(response => {
            console.log(response.data);
            setData(response.data.message);
        })
        .catch(err=>{
            console.error("Error fetching data:", err);
        })
    }, []);



    // useEffect(() => {
    //     fetch("http://localhost:3001/")
    //     .then(response => response.json())
    //     .then(data => {
    //         console.log(data);
    //     })
    //     .catch(err =>{
    //         console.error("Error fetching data:", err);
    //     })
    // }, []);

  return (
    <div>
      <h1>Welcome to the Home Page</h1>
      <p>This is a simple React component for the home page.</p>
        <p>Data from backend: {data}</p>

    </div>
  );
}
export default HomePage;