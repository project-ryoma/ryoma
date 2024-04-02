import { NextRequest, NextResponse } from "next/server";
import axios from "axios";
import { stringify } from "querystring";

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    const response = await fetch('http://localhost:3001/api/v1/chat/', {
      method: 'POST',
      body: JSON.stringify(body), 
      headers: {
        'Content-Type': 'application/json'
      }
    })
    const result = await response.json();
    return NextResponse.json(result); 
  } catch (err) {
    console.error(err);
    return NextResponse.error();
  }
}
