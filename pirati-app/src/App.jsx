import React from "react";
import { Button, Box, Heading } from "@chakra-ui/react";

function App() {
  return (
    <Box textAlign="center" py={10} px={6}>
      <Heading as="h1" size="2xl" mb={6}>
        Welcome to Chakra UI!
      </Heading>
      <Button colorScheme="teal" size="lg">
        Get Started
      </Button>
    </Box>
  );
}

export default App;
