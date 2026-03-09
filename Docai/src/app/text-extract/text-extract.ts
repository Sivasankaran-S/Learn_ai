import { Component, Inject, OnInit} from '@angular/core';
import { FormsModule } from '@angular/forms';
import { RouterOutlet } from '@angular/router';
import { MessageService } from 'primeng/api';
import { ButtonModule } from 'primeng/button';
import { DividerModule } from 'primeng/divider';
import { FileUploadModule, UploadEvent } from 'primeng/fileupload';
import { InputTextModule } from 'primeng/inputtext';
import { SelectModule } from 'primeng/select';
import { ToastModule } from 'primeng/toast';
import { CardModule } from 'primeng/card';
import { Api } from '../api';
import { CommonModule } from '@angular/common';
import { TableModule } from 'primeng/table';
import { InputGroup } from 'primeng/inputgroup';
import { InputGroupAddonModule } from 'primeng/inputgroupaddon';

@Component({
  selector: 'app-text-extract',
  imports: [
    ButtonModule,
    FileUploadModule,
    SelectModule,
    FormsModule,
    ToastModule,
    DividerModule,
    InputTextModule,
    CardModule,
    CommonModule,
    TableModule,
    InputGroup,
    InputGroupAddonModule
],
  templateUrl: './text-extract.html',
  styleUrl: './text-extract.css',
  providers:[MessageService,Api]
})
export class TextExtract implements OnInit {
  option :any = {}
  selectedOption : any = {}

  documentList : any = {}
  selectedDocumentList : any = {}
  messages : {text:string; sender: 'user' | 'bot'} [] = [];
  userMessages = '';
  ai_res = "";
  extractedData:any;
  ocrText : string = '';
  showData : boolean = false;
  show_pan : boolean = false;
  show_aadhaar : boolean = false;
  show_voterid : boolean = false;
  show_Driving_licence: boolean = false;
  showChat : boolean = false;
  showExtractedData : boolean = false;

  private readonly SESSION_ID = "session_id";
   constructor( private messageService: MessageService,private webapi : Api) {}
  ngOnInit(): void {
    //Called after the constructor, initializing input properties, and the first call to ngOnChanges.
    //Add 'implements OnInit' to the class.
    this.option = [
      {name:"Form-Filler",code:"1"},
      {name:"Query With Me?",code:"2"}
    ];
    
    this.documentList = [
      {name:"Aadhar Card",code:"A"},
      {name:"Pan Card",code:"P"},
      {name:"Voter-ID Card",code:"V"},
      {name:"Driving Lincense",code:"D"},
      {name:"Bank PassBook",code:"B"},
    ]
  }

  viewOption(){
    this.showData = false;
   if( this.selectedOption.code === "1") {
      this.showData = true
    }

  if(this.selectedOption.code === "2"){
    this.showChat = true;
  }
  }
   async sendMessages(){
    if(!this.userMessages.trim())
      return;
    const sessionId = sessionStorage.getItem(this.SESSION_ID); 
    console.log("Session_id:",sessionId);

    this.messages.push({text:this.userMessages , sender:'user'})
     const chatPayload = {
    session_id: sessionId,
    question: this.userMessages
  };
    const result =await  this.webapi.post("chat",chatPayload)
    if(result != null){
     let raw_ai_res = result.ai_res;
     this.ai_res = this.text_Filter(raw_ai_res);
      this.messages.push({text:this.ai_res,sender:'bot'})
    }
    // setTimeout(()=>{
    //   this.messages.push({text:'got it 👍',sender:'bot'})
    // })

    this.userMessages = " "
  }

 text_Filter(text: any): string {
  if (text === null || text === undefined) {
    return '';
  }

  // If already object or array → convert to string
  if (typeof text !== 'string') {
    text = JSON.stringify(text);
  }

  return text
    .replace(/```json|```/g, '')
    .replace(/[“”\u201c\u201d]/g, '"')
    .trim();
}

formatSummary(text: string): string {
  if (!text) return '';

  return text
    // Convert **bold** → <b>bold</b>
    .replace(/\*\*(.*?)\*\*/g, '<b>$1</b>')
    // Convert newlines → <br>
    .replace(/\n/g, '<br>');
}
 async OnUpload(event:any,fu:any) {
  const file = event.files[0];
  const doctype = this.selectedDocumentList.code;
  if(!doctype){
    this.messageService.add({
      severity:'warn',
      summary:'Selecion Requried',
      detail:"Please Select the document type"
    })
  return;
  }
  const formData = new FormData();
  formData.append('file',file)
  formData.append('doctype',doctype)
 const res = await this.webapi.post("uploadfiles",formData);
 console.log(event,"EVENT")
 if(res.status == "SUCCESS"){
    const result = res.Final_result;
    const doc_type = result.Doc_type;

      // 1. Get the raw string
      let rawString_Extract= result.Extracted_text;
     rawString_Extract=  this.text_Filter(rawString_Extract)
      let rawString_Ocr = result.Summarize;
      rawString_Ocr = this.formatSummary(rawString_Ocr)
    try {
      // 4. Parse the cleaned string
      this.extractedData = JSON.parse(rawString_Extract);
      this.ocrText = rawString_Ocr;
      this.messageService.add({ severity: 'success', summary: 'Success', detail: "Data Extracted" });
      this.showExtractedData = true;
      if (doc_type === "PAN"){
        
         this.show_pan = true
      }
      if(doc_type === "AADHAAR"){
        this.show_aadhaar = true
      }
      if(doc_type === "VOTERID"){
        this.show_voterid = true
      }
      if(doc_type === "DRIVING"){
        this.show_Driving_licence = true
      }
      sessionStorage.setItem(this.SESSION_ID,res.session_id)

    } catch (e) {
      console.error("Parsing error:", e);
      this.messageService.add({ 
        severity: 'error', 
        summary: 'Format Error', 
        detail: 'The extracted text format is invalid.' 
      });
  }
}
 }

 clear_data(){
  this.showData = false;
 }

}
