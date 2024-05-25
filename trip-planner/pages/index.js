import Head from 'next/head';
import TripForm from '../components/TripForm';


export default function Home() {
  return (
    <div className="container">
      <Head>
        <title>Trip Planner</title>
        <meta name="description" content="Plan your next trip effortlessly" />
        <link rel="icon" href="/favicon.ico" />
      </Head>
      <main>
        <h1>Welcome to the Trip Planner</h1>
        <TripForm />
      </main>
    </div>
  );
}
