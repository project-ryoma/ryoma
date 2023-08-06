import React, { useEffect, useState } from "react";
import Navbar from "../Navbar";
import axios from "axios";
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableContainer from '@mui/material/TableContainer';
import TableHead from '@mui/material/TableHead';
import TableRow from '@mui/material/TableRow';
import Paper from '@mui/material/Paper';
import "./job.scss";

function createData(
  id: number,
  job_name: string,
  job_status: string,
  job_start_time: string,
  job_type: string,
  job_engine: string
) {
  return { id, job_name, job_status, job_start_time, job_type, job_engine };
}

function Job() {

  // set state for table data rows
  const [rows, setRows] = useState<any[]>([]);

  const getJobHistory = async (): Promise<any[]> => {
  
    try {
      // Send a POST request to the API to retrieve the chat history
      const response = await axios.get('get_job_history');
  
      return response.data.map((row: any) => {
        // random generated id
        console.log(row);
        return createData(row.job_id, row.job_name, row.job_status, row.job_start_time, row.job_type, row.job_engine)
      });
    } catch (err) {
      console.error('Error fetching chat history:', err);
      throw err; // Rethrow the error to reject the Promise
    }
  }

  // Use useEffect to refresh the state when the page loads
  useEffect(() => {
    const refreshState = async () => {
      const newDataArray = await getJobHistory();
      setRows(newDataArray); // Update the state with the new data
    };

    refreshState(); // Call the refreshState function when the component mounts
  }, []); // Empty dependency array to run the effect only once on mount

  
  getJobHistory();
  console.log(rows);

  return (
    <div className="header">
      <div className="header__content">
        <Navbar />
      </div>
      <TableContainer component={Paper}>
      <Table className="log-table" sx={{ minWidth: 650 }} aria-label="simple table">
        <TableHead>
          <TableRow>
            <TableCell>Id</TableCell>
            <TableCell align="right">Job Name</TableCell>
            <TableCell align="right">Engine</TableCell>
            <TableCell align="right">Type&nbsp;(PDT)</TableCell>
            <TableCell align="right">Start Time</TableCell>
            <TableCell align="right">Status</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {rows.map((row) => (
            <TableRow
              key={row.id}
              sx={{ '&:last-child td, &:last-child th': { border: 0 } }}
            >
              <TableCell component="th" scope="row">
                {row.id}
              </TableCell>
              <TableCell align="right">{row.job_name}</TableCell>
              <TableCell align="right">{row.job_engine}</TableCell>
              <TableCell align="right">{row.job_type}</TableCell>
              <TableCell align="right">{row.job_start_time}</TableCell>
              <TableCell align="right">{row.job_status}</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
    </div>
  );
}

export default Job;