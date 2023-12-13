import { ChakraProvider } from '@chakra-ui/react'
import MainPage from './components/main_page/MainPage';


function App() {
  return (
    <ChakraProvider>
      <div>
        <MainPage />
      </div>
    </ChakraProvider>
  );
}

export default App;
