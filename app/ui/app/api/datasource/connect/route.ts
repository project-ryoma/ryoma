import { NextRequest, NextResponse } from "next/server";
import axios from "axios";

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    const response = await axios.post(
      "http://localhost:3001/api/v1/datasource/connect", body
    );
    return NextResponse.json(response.data); 
  } catch (err) {
    return NextResponse.error();
  }
}
