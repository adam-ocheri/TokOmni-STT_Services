import { ChakraProvider } from '@chakra-ui/react'
import MainPage from './components/main_page/MainPage';
import './App.css'
// import { config } from 'dotenv'
import { useEffect } from 'react';


function App() {

  useEffect(() => {
    // config();
  }, [])

  return (
    <ChakraProvider>
      <div>
        <MainPage />
      </div>
    </ChakraProvider>
  );
}

export default App;
