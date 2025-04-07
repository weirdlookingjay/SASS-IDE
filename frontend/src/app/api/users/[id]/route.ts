import { NextRequest, NextResponse } from 'next/server';

export async function GET(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const userId = params.id;
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001';

    // Convert numeric ID to user details
    const response = await fetch(`${apiUrl}/api/users/${userId}`);
    if (!response.ok) {
      return new NextResponse(null, {
        status: response.status,
        statusText: response.statusText
      });
    }

    const data = await response.json();
    return NextResponse.json({
      id: data.id,
      username: data.username,
      name: `${data.first_name} ${data.last_name}`.trim(),
      email: data.email
    });
  } catch (error) {
    console.error('Error in users API:', error);
    return new NextResponse(null, {
      status: 500,
      statusText: 'Internal Server Error'
    });
  }
}
