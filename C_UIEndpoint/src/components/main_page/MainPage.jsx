import {useEffect, useState} from 'react'
import axios from "axios";

// const baseAPI_URL = process?.env?.RUNTIME_ENV == 'production' ? `http://127.0.0.1` : `http://localhost`;
// console.log("BaseAPIURL is: ", baseAPI_URL);
const baseAPI_URL = `http://127.0.0.1`;
// const baseAPI_URL = `http://backend-server`;

export default function MainPage() {

    const [filename, setFilename] = useState('');
    const [conversation, setConversation] = useState([]);

    useEffect(()=> {
        
    }, [])

    function onTextChanged(e) {
        setFilename(e.target.value)
    }

    async function onTranscribeStart(){
        if (filename === "") return;

        const file = filename
        const url = `${baseAPI_URL}:5000/request_transcription_work/`;
        const headers = {
            'Content-Type': 'application/json',
        };
        try {
            const response = await axios.get(url + file, { headers });
            console.log("Got some response!")
            console.log(response)
            if(response?.data?.fullTranscript)
            {
                setConversation(response.data.fullTranscript);
            }
        } catch (error) {
            throw new Error(error)
        }
    }

    return (
        <div style={{display: 'flex', flexDirection: 'column', alignContent: 'center', backgroundColor: 'grey'}}>
            <input type={'text'} value={filename} onChange={(e)=>{onTextChanged(e)}}/>
            <button onClick={async ()=>{await onTranscribeStart()}}>Start</button>

            {conversation.length > 0 && 
            <div style={{background: 'grey'}}>
                <h2>Conversation Result</h2>
                {conversation.map((item, idx) => (<div key={idx}>
                    <section style={{
                        background: item.speaker === "ServicePerson" ? 'green' : 'orange',
                        display: 'flex',
                        flexDirection: 'column',
                        alignContent: 'center',
                        textAlign: 'center',
                        border: '2px solid black',
                        borderRadius: '12px',
                        margin: '10px',
                        paddingLeft: item.speaker === "ServicePerson" ? '100px' : '0',
                        paddingRight: item.speaker !== "ServicePerson" ? '100px' : '0',
                    }}>
                        <h3>{item.speaker}</h3>
                        <p>
                            {item.text}
                        </p>
                    </section>
                </div>))}
            </div>
            }
        </div>
    )
}
