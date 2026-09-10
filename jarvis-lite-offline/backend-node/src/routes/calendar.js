import express from 'express'
import { google } from 'googleapis'
import dotenv from 'dotenv'
import fs from 'fs'
import path from 'path'
dotenv.config()
const router=express.Router()
const DATA_DIR=path.resolve(process.env.DATA_DIR||'./data')
const TOKEN_FILE=path.join(DATA_DIR,'google-tokens.json')
fs.mkdirSync(DATA_DIR,{recursive:true})
const oauth2Client=new google.auth.OAuth2(process.env.GOOGLE_CLIENT_ID,process.env.GOOGLE_CLIENT_SECRET,process.env.GOOGLE_REDIRECT_URI||'http://localhost:5000/api/calendar/callback')
let tokens=null
try { tokens=JSON.parse(fs.readFileSync(TOKEN_FILE,'utf8')); oauth2Client.setCredentials(tokens) } catch {}
function saveTokens(){ fs.writeFileSync(TOKEN_FILE,JSON.stringify(tokens,null,2)) }
async function getCalendar(){ if(!tokens) return null; oauth2Client.setCredentials(tokens); return google.calendar({version:'v3',auth:oauth2Client}) }
router.get('/status',(req,res)=>res.json({connected:!!tokens}))
router.get('/auth',(req,res)=>res.redirect(oauth2Client.generateAuthUrl({access_type:'offline',prompt:'consent',scope:['https://www.googleapis.com/auth/calendar']})))
router.get('/callback',async(req,res)=>{ try { const {tokens:t}=await oauth2Client.getToken(req.query.code); tokens=t; saveTokens(); oauth2Client.setCredentials(t); res.send('<h2>Calendar connected.</h2><p>You can close this tab.</p>') } catch(e){ res.status(400).send('Calendar authorization failed.') } })
router.get('/events/today',async(req,res)=>{ try { const calendar=await getCalendar(); if(!calendar) return res.status(401).json({error:'not connected'}); const start=new Date(); start.setHours(0,0,0,0); const end=new Date(); end.setHours(23,59,59,999); const r=await calendar.events.list({calendarId:'primary',timeMin:start.toISOString(),timeMax:end.toISOString(),singleEvents:true,orderBy:'startTime'}); res.json((r.data.items||[]).map(e=>({id:e.id,summary:e.summary||'(untitled)',start:e.start.dateTime||e.start.date,end:e.end.dateTime||e.end.date}))) } catch(e){ res.status(500).json({error:e.message}) } })
router.post('/events',async(req,res)=>{ try { const calendar=await getCalendar(); if(!calendar) return res.status(401).json({error:'not connected'}); const {title,start,end,description='',location=''}=req.body; if(!title||!start||!end) return res.status(400).json({error:'title, start and end are required'}); const r=await calendar.events.insert({calendarId:'primary',requestBody:{summary:title,description,location,start:{dateTime:new Date(start).toISOString()},end:{dateTime:new Date(end).toISOString()}}}); res.status(201).json({id:r.data.id,summary:r.data.summary,start:r.data.start?.dateTime,end:r.data.end?.dateTime}) } catch(e){ res.status(500).json({error:e.message}) } })
export default router
